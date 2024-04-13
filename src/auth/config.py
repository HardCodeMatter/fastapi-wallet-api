from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def SECRET_KEY(self) -> str:
        return f'{self.SECRET_KEY}'
    
    @property
    def ALGORITHM(self) -> str:
        return f'{self.ALGORITHM}'
    
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='allow',
    )


auth_settings = AuthSettings()
