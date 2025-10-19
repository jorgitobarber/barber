from sqlalchemy import text

def upgrade():
    # Agregar columna tip a la tabla sales
    op.add_column('sales', 
        Column('tip', Float, default=0.0, nullable=False, server_default='0.0')
    )

def downgrade():
    # Eliminar columna tip si se revierte la migración
    op.drop_column('sales', 'tip')
