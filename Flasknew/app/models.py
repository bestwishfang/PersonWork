from . import models


class BaseModel(models.Model):
    __abstract__ = True  # 声明当前类是抽象类，被继承调用不被创建
    id = models.Column(models.Integer, primary_key=True, autoincrement=True)

    def save(self):
        db = models.session()
        db.add(self)
        db.commit()

    def delete(self):
        db = models.session()
        db.delete(self)
        db.commit()


class User(BaseModel):
    __tablename__ = "user"
    user_name = models.Column(models.String(32))
    password = models.Column(models.String(32))
    email = models.Column(models.String(32))


class Leave(BaseModel):
    """
    请假  0
    批准  1
    驳回  2
    销假  3
    """
    __tablename__ = "leave"
    request_id = models.Column(models.Integer)  # 请假人id
    request_name = models.Column(models.String(32))  # 请假人姓名
    request_type = models.Column(models.String(32))  # 假期类型
    request_start_time = models.Column(models.String(32))  # 起始时间
    request_end_time = models.Column(models.String(32))  # 结束时间
    request_description = models.Column(models.Text)  # 请假事由
    request_phone = models.Column(models.String(32))  # 联系方式
    request_status = models.Column(models.String(32))  # 假条状态
