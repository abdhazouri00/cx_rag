from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy import select, insert, func, delete

class AssetModel(BaseDataModel):
  def __init__(self,db_client:object):
    super().__init__(db_client=db_client)
    self.db_client = db_client

  @classmethod
  async def create_instance(cls,db_client:object):
    instance = cls(db_client)
    return instance
  
  async def create_asset(self, asset:Asset):
    async with self.db_client() as session:
      async with session.begin():
        session.add(asset)
      await session.commit()
      await session.refresh(asset)

    return asset
  
  async def get_all_assets(self, asset_type:str):
    async with self.db_client() as session:
      statement = select(Asset).where(Asset.asset_type == asset_type).order_by(Asset.asset_id)
      result = await session.execute(statement)
      records = result.scalars().all()
    return records

  async def get_asset_records(self, asset_name: str):
    async with self.db_client() as session:
      statement = select(Asset).where(Asset.asset_name == asset_name)
      result = await session.execute(statement)
      record = result.scalar_one_or_none()
    return record