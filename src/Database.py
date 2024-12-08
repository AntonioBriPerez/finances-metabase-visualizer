import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging


class Database:
    def __init__(self, host, port, database, user, password, schema="public"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.schema = schema

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def _create_engine(self):
        try:
            engine = create_engine(self.connection_string)
            return engine
        except Exception as e:
            self.logger.error(f"Error al crear el motor de conexión: {e}")
            raise

    def insert_dataframe(self, dataframe, table_name, if_exists="append", index=False):
        try:
            if not isinstance(dataframe, pd.DataFrame):
                raise ValueError("El argumento debe ser un DataFrame de pandas")

            engine = self._create_engine()
            with engine.connect() as connection:
                rows_inserted = dataframe.to_sql(
                    name=table_name,
                    con=connection,
                    schema=self.schema,
                    if_exists=if_exists,
                    index=index,
                )

            self.logger.info(
                f"Se insertaron {rows_inserted} filas en la tabla {table_name}"
            )
            return rows_inserted

        except SQLAlchemyError as sql_error:
            self.logger.error(f"Error de SQLAlchemy al insertar datos: {sql_error}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al insertar datos: {e}")
            raise

    def get_existing_hashes(self, table_name):
        try:
            engine = self._create_engine()
            with engine.connect() as connection:
                query = text(f"SELECT hash_fichero FROM {self.schema}.{table_name}")
                result = connection.execute(query)
                hashes = [row[0] for row in result]

            self.logger.info(
                f"Se obtuvieron {len(hashes)} hashes de la tabla {table_name}"
            )
            return hashes

        except SQLAlchemyError as sql_error:
            self.logger.error(f"Error de SQLAlchemy al obtener hashes: {sql_error}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al obtener hashes: {e}")
            raise

    def test_connection(self):
        try:
            engine = self._create_engine()
            with engine.connect() as connection:
                self.logger.info("Conexión a la base de datos exitosa")
                return True
        except Exception as e:
            self.logger.error(f"Error de conexión: {e}")
            return False
