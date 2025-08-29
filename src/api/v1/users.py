import datetime

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List

from src.core.dependencies.db_dependency import db_manager
from src.schemas.user_schemas import UserCreate, UserResponse, TransferCreate, TransferResponse


router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate = Body(UserCreate)) -> UserResponse:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким email уже существует"
            )
        
        cursor.execute(
            "INSERT INTO users (name, email, balance, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (user_data.name, user_data.email, user_data.balance, now, now)
        )
        conn.commit()
        
        # Получаем ID созданного пользователя
        user_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        created_user = cursor.fetchone()
        
        if not created_user:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при создании пользователя"
            )
            
        return {
            'id': created_user[0],
            'name': created_user[1],
            'email': created_user[2],
            'balance': created_user[3],
            'created_at': created_user[4],
            'updated_at': created_user[5],
        }


@router.get("/users", response_model=List[UserResponse])
async def get_users() -> List[UserResponse]:
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        return [
            {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'balance': user[3],
                'created_at': user[4],
                'updated_at': user[5],
            } for user in users
        ]


@router.post("/transfer", response_model=TransferResponse, status_code=201)
async def make_transfer(transfer_data: TransferCreate = Body(TransferCreate)) -> TransferResponse:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if transfer_data.from_user_id == transfer_data.to_user_id:
        raise HTTPException(
            status_code=400,
            detail="Нельзя переводить деньги самому себе"
        )
    
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, balance FROM users WHERE id = ?", (transfer_data.from_user_id,))
        from_user = cursor.fetchone()
        
        if not from_user:
            raise HTTPException(
                status_code=404,
                detail="Отправитель не найден"
            )
        
        if from_user[1] < transfer_data.amount:
            raise HTTPException(
                status_code=400,
                detail="Недостаточно средств для перевода"
            )
        
        cursor.execute("SELECT id FROM users WHERE id = ?", (transfer_data.to_user_id,))
        to_user = cursor.fetchone()
        
        if not to_user:
            raise HTTPException(
                status_code=404,
                detail="Получатель не найден"
            )
        
        try:
            cursor.execute(
                "UPDATE users SET balance = balance - ?, updated_at = ? WHERE id = ?",
                (transfer_data.amount, now, transfer_data.from_user_id)
            )
            
            cursor.execute(
                "UPDATE users SET balance = balance + ?, updated_at = ? WHERE id = ?",
                (transfer_data.amount, now, transfer_data.to_user_id)
            )

            cursor.execute(
                "INSERT INTO transfers (from_user_id, to_user_id, amount, created_at) VALUES (?, ?, ?, ?)",
                (transfer_data.from_user_id, transfer_data.to_user_id, transfer_data.amount, now)
            )
            
            conn.commit()
            
            # Получаем ID созданного перевода
            transfer_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM transfers WHERE id = ?", (transfer_id,))
            created_transfer = cursor.fetchone()
            
            return {
                'id': created_transfer[0],
                'from_user_id': created_transfer[1],
                'to_user_id': created_transfer[2],
                'amount': created_transfer[3],
                'created_at': created_transfer[4],
            }
            
        except Exception as e:
            conn.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при выполнении перевода: {str(e)}"
            )
