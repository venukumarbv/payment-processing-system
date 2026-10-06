from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.transaction import TopMerchantResponse, TransactionResponse
from src.repository.read_repo import ReadRepository
from src.routers.auth import get_current_user
from src.routers.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router, tags=["Authentication"])


@api_router.get(
    "/transaction/{txn_id}", tags=["Transactions"], response_model=TransactionResponse
)
async def get_transactions(
    txn_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Fetch full details for a specific transactions
    """
    repo = ReadRepository(db)

    result = repo.get_transactions(txn_id=txn_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {txn_id} not found",
        )

    if hasattr(result, "_mapping"):
        return result._mapping
    return result


@api_router.get(
    "/merchants/top", tags=["Analytics"], response_model=List[TopMerchantResponse]
)
async def read_top_merchants(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Returns Top 5 Merchants ranked by Total Transaction Amount within specified date range
    """
    # Initialize the read repository
    repo = ReadRepository(db)

    try:
        # Execute the optimized aggregation query
        results = repo.get_top_merchants(start_date, end_date)

        # Convert the SQL rows into a list of dictionaries for the response model
        return [dict(row._mapping) for row in results]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTPDynamics_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching top merchants: {str(e)}",
        )
