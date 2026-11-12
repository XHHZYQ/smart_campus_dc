"""公共依赖模块：登录态解析与角色校验。

前端在请求头中携带 Authorization: Bearer <token>，
后端通过 get_current_user 解析出当前登录用户，
再通过 require_roles 做角色级访问控制。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SysUser
from app.security import decode_access_token

# 使用 Bearer 方案解析令牌，auto_error=False 便于自定义错误信息
bearer_scheme = HTTPBearer(auto_error=False)

# 角色编码常量
ROLE_ADMIN = "admin"                  # 系统管理员
ROLE_ACADEMIC = "academic"            # 教务管理员
ROLE_HEAD_TEACHER = "head_teacher"    # 班主任
ROLE_SUBJECT_TEACHER = "subject_teacher"  # 任课教师
ROLE_GENERAL_AFFAIRS = "general_affairs"  # 总务管理员


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> SysUser:
    """解析令牌并返回当前登录用户对象。"""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录状态已失效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or not credentials.credentials:
        raise unauthorized

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise unauthorized

    user_id = payload.get("sub")
    if user_id is None:
        raise unauthorized

    user = db.get(SysUser, int(user_id))
    if user is None:
        raise unauthorized

    if user.status != "启用":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被停用，请联系管理员"
        )
    return user


def require_roles(*role_codes: str):
    """生成角色校验依赖：仅允许指定角色访问。"""

    def checker(current_user: SysUser = Depends(get_current_user)) -> SysUser:
        if role_codes and current_user.role.code not in role_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="当前角色无权访问该功能",
            )
        return current_user

    return checker
