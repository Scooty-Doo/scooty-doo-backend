"""Create tables

Revision ID: 3438d9f7e26b
Revises: 
Create Date: 2024-12-12 10:59:30.182342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3438d9f7e26b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_name', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role_name')
    )
    op.create_table('admins',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('full_name', sa.Text(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_geospatial_table('cities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city_name', sa.Text(), nullable=False),
    sa.Column('country_code', sa.CHAR(length=3), nullable=False),
    sa.Column('c_location', Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_geospatial_index('idx_cities_c_location', 'cities', ['c_location'], unique=False, postgresql_using='gist', postgresql_ops={})
    op.create_table('payment_providers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider_name', sa.Text(), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider_name')
    )
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('full_name', sa.Text(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('use_prepay', sa.Boolean(), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('zone_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type_name', sa.Text(), nullable=False),
    sa.Column('speed_limit', sa.Integer(), nullable=True),
    sa.Column('start_fee', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('end_fee', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type_name')
    )
    op.create_table('admin_2_admin_roles',
    sa.Column('admin_id', sa.BigInteger(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['admin_roles.id'], ),
    sa.PrimaryKeyConstraint('admin_id', 'role_id')
    )
    op.create_geospatial_table('bikes',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('battery_lvl', sa.Integer(), nullable=False),
    sa.Column('last_position', Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('battery_lvl >= 0 AND battery_lvl <= 100', name='battery_level_check'),
    sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_geospatial_index('idx_bikes_last_position', 'bikes', ['last_position'], unique=False, postgresql_using='gist', postgresql_ops={})
    op.create_geospatial_table('map_zones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('zone_name', sa.Text(), nullable=False),
    sa.Column('zone_type_id', sa.Integer(), nullable=False),
    sa.Column('city_id', sa.Integer(), nullable=False),
    sa.Column('boundary', Geometry(geometry_type='POLYGON', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
    sa.ForeignKeyConstraint(['zone_type_id'], ['zone_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_geospatial_index('idx_map_zones_boundary', 'map_zones', ['boundary'], unique=False, postgresql_using='gist', postgresql_ops={})
    op.create_table('payment_methods',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.Column('provider_specific_id', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['provider_id'], ['payment_providers.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_geospatial_table('trips',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('bike_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('start_position', Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
    sa.Column('end_position', Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.Column('path_taken', Geometry(geometry_type='LINESTRING', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.Column('start_fee', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('time_fee', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('end_fee', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('total_fee', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bike_id'], ['bikes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_geospatial_index('idx_trips_end_position', 'trips', ['end_position'], unique=False, postgresql_using='gist', postgresql_ops={})
    op.create_geospatial_index('idx_trips_path_taken', 'trips', ['path_taken'], unique=False, postgresql_using='gist', postgresql_ops={})
    op.create_geospatial_index('idx_trips_start_position', 'trips', ['start_position'], unique=False, postgresql_using='gist', postgresql_ops={})
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('transaction_type', sa.Text(), nullable=False),
    sa.Column('transaction_description', sa.Text(), nullable=True),
    sa.Column('trip_id', sa.BigInteger(), nullable=True),
    sa.Column('payment_method_id', sa.Integer(), nullable=True),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ),
    sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_geospatial_index('idx_trips_start_position', table_name='trips', postgresql_using='gist', column_name='start_position')
    op.drop_geospatial_index('idx_trips_path_taken', table_name='trips', postgresql_using='gist', column_name='path_taken')
    op.drop_geospatial_index('idx_trips_end_position', table_name='trips', postgresql_using='gist', column_name='end_position')
    op.drop_geospatial_table('trips')
    op.drop_table('payment_methods')
    op.drop_geospatial_index('idx_map_zones_boundary', table_name='map_zones', postgresql_using='gist', column_name='boundary')
    op.drop_geospatial_table('map_zones')
    op.drop_geospatial_index('idx_bikes_last_position', table_name='bikes', postgresql_using='gist', column_name='last_position')
    op.drop_geospatial_table('bikes')
    op.drop_table('admin_2_admin_roles')
    op.drop_table('zone_types')
    op.drop_table('users')
    op.drop_table('payment_providers')
    op.drop_geospatial_index('idx_cities_c_location', table_name='cities', postgresql_using='gist', column_name='c_location')
    op.drop_geospatial_table('cities')
    op.drop_table('admins')
    op.drop_table('admin_roles')
    # ### end Alembic commands ###