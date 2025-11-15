import os
from datetime import datetime, timedelta
import pandas as pd
import bcrypt

# Paths e constantes
USERS_PATH = os.getenv("USERS_PARQUET_PATH", "data/users.parquet")
MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15
SESSAO_MINUTOS = 30


def init_db():
    """Compat layer: cria store de usuários se não existir."""
    init_store()


def init_store():
    parent = os.path.dirname(USERS_PATH)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    if not os.path.exists(USERS_PATH):
        df = pd.DataFrame(
            columns=[
                "username",
                "password_hash",
                "role",
                "ativo",
                "tentativas_invalidas",
                "bloqueado_ate",
                "ultimo_login",
            ]
        )
        df.to_parquet(USERS_PATH, index=False)


def _read_df():
    init_store()
    return pd.read_parquet(USERS_PATH)


def _write_df(df):
    df.to_parquet(USERS_PATH, index=False)


def criar_usuario(username, password, role="user"):
    df = _read_df()
    if username in df["username"].values:
        raise ValueError("Usuário já existe")
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    row = {
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "ativo": True,
        "tentativas_invalidas": 0,
        "bloqueado_ate": pd.NaT,
        "ultimo_login": pd.NaT,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _write_df(df)


def autenticar_usuario(username, password):
    df = _read_df()
    user = df[df["username"] == username]
    if user.empty:
        return None, "Usuário não encontrado"
    user = user.iloc[0]
    if not bool(user.get("ativo", True)):
        return None, "Usuário inativo ou bloqueado"
    bloqueado_ate = user.get("bloqueado_ate")
    if pd.notna(bloqueado_ate):
        if datetime.now() < pd.to_datetime(bloqueado_ate):
            return None, f"Usuário bloqueado até {bloqueado_ate}"

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        idx = df.index[df["username"] == username][0]
        prev = int(user.get("tentativas_invalidas", 0))
        df.at[idx, "tentativas_invalidas"] = prev + 1
        if df.at[idx, "tentativas_invalidas"] >= MAX_TENTATIVAS:
            df.at[idx, "bloqueado_ate"] = (
                datetime.now() + timedelta(minutes=BLOQUEIO_MINUTOS)
            )
        _write_df(df)
        if df.at[idx, "tentativas_invalidas"] >= MAX_TENTATIVAS:
            return None, (
                f"Usuário bloqueado por {BLOQUEIO_MINUTOS} minutos"
            )
        remaining = MAX_TENTATIVAS - df.at[idx, "tentativas_invalidas"]
        return None, f"Senha incorreta. Tentativas restantes: {remaining}"

    idx = df.index[df["username"] == username][0]
    df.at[idx, "tentativas_invalidas"] = 0
    df.at[idx, "bloqueado_ate"] = pd.NaT
    df.at[idx, "ultimo_login"] = datetime.now()
    _write_df(df)
    return user.get("role", "user"), None


def solicitar_redefinicao(username):
    df = _read_df()
    idxs = df.index[df["username"] == username]
    if idxs.empty:
        raise ValueError("Usuário não encontrado")
    idx = idxs[0]
    df.at[idx, "redefinir_solicitado"] = True
    _write_df(df)


def aprovar_redefinicao(username):
    df = _read_df()
    idxs = df.index[df["username"] == username]
    if idxs.empty:
        raise ValueError("Usuário não encontrado")
    idx = idxs[0]
    df.at[idx, "redefinir_aprovado"] = True
    _write_df(df)


def redefinir_senha(username, nova_senha):
    df = _read_df()
    idxs = df.index[df["username"] == username]
    if idxs.empty:
        raise ValueError("Usuário não encontrado")
    idx = idxs[0]
    if not df.at[idx, "redefinir_aprovado"]:
        raise ValueError("Redefinição não aprovada")
    password_hash = bcrypt.hashpw(
        nova_senha.encode(), bcrypt.gensalt()
    ).decode()
    df.at[idx, "password_hash"] = password_hash
    df.at[idx, "redefinir_solicitado"] = False
    df.at[idx, "redefinir_aprovado"] = False
    _write_df(df)


def sessao_expirada(ultimo_login):
    if not ultimo_login:
        return True
    if not isinstance(ultimo_login, datetime):
        return True
    return (datetime.now() - ultimo_login) > timedelta(minutes=SESSAO_MINUTOS)
