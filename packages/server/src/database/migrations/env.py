from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig( config.config_file_name )

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# TODO: Đơn giản và linh hoạt hóa đoạn code này 
# để có thể thực hiện migration từ bất kì vị trí nào trong project 

import sys, os
from pathlib import Path

# Thêm thư mục src vào Python path
current_dir = Path(__file__).parent  # Thư mục migrations
src_dir = current_dir.parent.parent  # Lên 2 cấp để đến src
sys.path.insert(0, str(src_dir))

print(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[2]))

import sys
import os
from pathlib import Path

# Debug thông tin hiện tại
print("Current working directory:", os.getcwd())

# Tính toán đường dẫn đến thư mục src
# Từ database/migrations, chúng ta cần lên 1 cấp để đến src
current_file_dir = Path(__file__).parent  # Thư mục migrations
database_dir = current_file_dir.parent    # Thư mục database  
src_dir = database_dir.parent             # Thư mục src

# Thêm src directory vào Python path
sys.path.insert(0, str(src_dir))

print("Added to Python path:", str(src_dir))
print("Updated Python path:", sys.path[:3])  # Chỉ hiển thị 3 đường dẫn đầu tiên

import sys
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print("File location:", __file__)

from database.entities.utils.base import Base
from database.entities.attendance import EmployeeAttendance

def get_metadata():
    return Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

from database.engine import build_postgres_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = build_postgres_url()
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # connectable = engine_from_config(
    #     config.get_section( config.config_ini_section, {} ),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    configuration = config.get_section(config.config_ini_section)
    configuration[ "sqlalchemy.url" ] = build_postgres_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=get_metadata()
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
