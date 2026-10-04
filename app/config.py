import os
import configparser

PROPERTIES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.properties')

class AppConfig:
    def __init__(self, properties_file=PROPERTIES_FILE):
        self.properties_file = properties_file
        self.load_config()

    def load_config(self):
        self.properties = {}
        if os.path.exists(self.properties_file):
            with open(self.properties_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        self.properties[k.strip()] = v.strip()

    def get(self, key, default=None):
        return self.properties.get(key, default)

    def set(self, key, value):
        self.properties[key] = str(value)

    def save(self):
        lines = []
        if os.path.exists(self.properties_file):
            with open(self.properties_file, 'r') as f:
                lines = f.readlines()

        updated_keys = set()
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                k, v = stripped.split('=', 1)
                k = k.strip()
                if k in self.properties:
                    new_lines.append(f"{k}={self.properties[k]}\n")
                    updated_keys.add(k)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        for k, v in self.properties.items():
            if k not in updated_keys:
                new_lines.append(f"{k}={v}\n")

        with open(self.properties_file, 'w') as f:
            f.writelines(new_lines)

    @property
    def sqlalchemy_database_uri(self):
        db_type = self.get('db.type', 'sqlite').lower()
        if db_type == 'oracle':
            host = self.get('db.host', 'localhost')
            port = self.get('db.port', '1521')
            service_name = self.get('db.name', 'XE')
            user = self.get('db.user', 'system')
            pwd = self.get('db.password', 'oracle')
            return f"oracle+cx_oracle://{user}:{pwd}@{host}:{port}/?service_name={service_name}"
        elif db_type == 'postgresql' or db_type == 'postgres':
            host = self.get('db.host', 'localhost')
            port = self.get('db.port', '5432')
            dbname = self.get('db.name', 'cth_report_db')
            user = self.get('db.user', 'postgres')
            pwd = self.get('db.password', 'postgres')
            return f"postgresql://{user}:{pwd}@{host}:{port}/{dbname}"
        elif db_type == 'sqlserver':
            host = self.get('db.host', 'localhost')
            port = self.get('db.port', '1433')
            dbname = self.get('db.name', 'cth_report_db')
            user = self.get('db.user', 'sa')
            pwd = self.get('db.password', 'Password123!')
            return f"mssql+pyodbc://{user}:{pwd}@{host}:{port}/{dbname}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            # Fallback to SQLite
            sqlite_path = self.get('db.sqlite_path', 'db/cth_app.db')
            base_dir = os.path.dirname(os.path.dirname(__file__))
            abs_path = os.path.join(base_dir, sqlite_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            return f"sqlite:///{abs_path}"

config = AppConfig()
