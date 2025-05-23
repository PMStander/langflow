from typing import Annotated, List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import func, desc, and_, or_, text
from sqlmodel import select, col

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import Workspace, WorkspaceMember
from langflow.services.database.models.crm.client import Client
from langflow.services.database.models.crm.invoice import Invoice
from langflow.services.database.models.crm.opportunity import Opportunity
from langflow.services.database.models.crm.task import Task
from langflow.services.database.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])

class ReportType(str, Enum):
    """Report types for CRM reporting."""
    SALES_OVERVIEW = "sales_overview"
    CLIENT_ACTIVITY = "client_activity"
    OPPORTUNITY_PIPELINE = "opportunity_pipeline"
    INVOICE_AGING = "invoice_aging"
    TASK_COMPLETION = "task_completion"
    REVENUE_FORECAST = "revenue_forecast"
    CUSTOM = "custom"

class TimeFrame(str, Enum):
    """Time frames for report filtering."""
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    LAST_12_MONTHS = "last_12_months"
    YEAR_TO_DATE = "year_to_date"
    CUSTOM = "custom"

class ExportFormat(str, Enum):
    """Export formats for report data."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"

@router.get("/types", status_code=200)
async def get_report_types():
    """Get available report types."""
    return {
        "report_types": [
            {
                "id": ReportType.SALES_OVERVIEW,
                "name": "Sales Overview",
                "description": "Overview of sales performance including revenue, invoices, and opportunities.",
                "metrics": ["total_revenue", "average_deal_size", "win_rate", "sales_cycle_length"]
            },
            {
                "id": ReportType.CLIENT_ACTIVITY,
                "name": "Client Activity",
                "description": "Analysis of client engagement and activity.",
                "metrics": ["active_clients", "new_clients", "client_retention", "client_conversion"]
            },
            {
                "id": ReportType.OPPORTUNITY_PIPELINE,
                "name": "Opportunity Pipeline",
                "description": "Analysis of the sales pipeline and opportunity stages.",
                "metrics": ["pipeline_value", "stage_distribution", "conversion_rates", "average_time_in_stage"]
            },
            {
                "id": ReportType.INVOICE_AGING,
                "name": "Invoice Aging",
                "description": "Analysis of outstanding invoices and payment patterns.",
                "metrics": ["outstanding_amount", "overdue_invoices", "average_payment_time", "payment_rate"]
            },
            {
                "id": ReportType.TASK_COMPLETION,
                "name": "Task Completion",
                "description": "Analysis of task completion rates and efficiency.",
                "metrics": ["completion_rate", "average_completion_time", "overdue_tasks", "task_distribution"]
            },
            {
                "id": ReportType.REVENUE_FORECAST,
                "name": "Revenue Forecast",
                "description": "Forecast of future revenue based on pipeline and historical data.",
                "metrics": ["projected_revenue", "forecast_accuracy", "growth_rate", "seasonal_patterns"]
            },
            {
                "id": ReportType.CUSTOM,
                "name": "Custom Report",
                "description": "Create a custom report with selected metrics and dimensions.",
                "metrics": ["custom"]
            }
        ],
        "time_frames": [
            {"id": TimeFrame.LAST_7_DAYS, "name": "Last 7 Days"},
            {"id": TimeFrame.LAST_30_DAYS, "name": "Last 30 Days"},
            {"id": TimeFrame.LAST_90_DAYS, "name": "Last 90 Days"},
            {"id": TimeFrame.LAST_12_MONTHS, "name": "Last 12 Months"},
            {"id": TimeFrame.YEAR_TO_DATE, "name": "Year to Date"},
            {"id": TimeFrame.CUSTOM, "name": "Custom Date Range"}
        ],
        "export_formats": [
            {"id": ExportFormat.JSON, "name": "JSON"},
            {"id": ExportFormat.CSV, "name": "CSV"},
            {"id": ExportFormat.EXCEL, "name": "Excel"}
        ]
    }

@router.get("/{report_type}", status_code=200)
async def generate_report(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    report_type: ReportType,
    workspace_id: UUID,
    time_frame: TimeFrame = TimeFrame.LAST_30_DAYS,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    client_id: Optional[UUID] = None,
    export_format: Optional[ExportFormat] = None,
    metrics: List[str] = Query(None),
    dimensions: List[str] = Query(None),
    filters: Optional[str] = None
):
    """Generate a report based on the specified type and parameters."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        # Calculate date range based on time_frame
        now = datetime.now(timezone.utc)
        if time_frame == TimeFrame.CUSTOM:
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom time frame requires start_date and end_date",
                )
            date_from = start_date
            date_to = end_date
        elif time_frame == TimeFrame.LAST_7_DAYS:
            date_from = now - timedelta(days=7)
            date_to = now
        elif time_frame == TimeFrame.LAST_30_DAYS:
            date_from = now - timedelta(days=30)
            date_to = now
        elif time_frame == TimeFrame.LAST_90_DAYS:
            date_from = now - timedelta(days=90)
            date_to = now
        elif time_frame == TimeFrame.LAST_12_MONTHS:
            date_from = now - timedelta(days=365)
            date_to = now
        elif time_frame == TimeFrame.YEAR_TO_DATE:
            date_from = datetime(now.year, 1, 1, tzinfo=timezone.utc)
            date_to = now
        
        # Parse filters if provided
        filter_conditions = {}
        if filters:
            try:
                filter_conditions = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid filter format. Must be valid JSON.",
                )
        
        # Generate report based on type
        if report_type == ReportType.SALES_OVERVIEW:
            report_data = await generate_sales_overview(session, workspace_id, date_from, date_to, client_id, filter_conditions)
        elif report_type == ReportType.CLIENT_ACTIVITY:
            report_data = await generate_client_activity(session, workspace_id, date_from, date_to, client_id, filter_conditions)
        elif report_type == ReportType.OPPORTUNITY_PIPELINE:
            report_data = await generate_opportunity_pipeline(session, workspace_id, date_from, date_to, client_id, filter_conditions)
        elif report_type == ReportType.INVOICE_AGING:
            report_data = await generate_invoice_aging(session, workspace_id, date_from, date_to, client_id, filter_conditions)
        elif report_type == ReportType.TASK_COMPLETION:
            report_data = await generate_task_completion(session, workspace_id, date_from, date_to, client_id, filter_conditions)
        elif report_type == ReportType.REVENUE_FORECAST:
            report_data = await generate_revenue_forecast(session, workspace_id, date_from, date_to, client_id, filter_conditions)
        elif report_type == ReportType.CUSTOM:
            if not metrics:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom report requires at least one metric",
                )
            report_data = await generate_custom_report(session, workspace_id, date_from, date_to, metrics, dimensions, client_id, filter_conditions)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported report type: {report_type}",
            )
        
        # Export data if format specified
        if export_format:
            return export_report_data(report_data, export_format, f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        return report_data
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e

# Helper functions for report generation
async def generate_sales_overview(session, workspace_id, date_from, date_to, client_id=None, filters=None):
    """Generate sales overview report."""
    # Base query conditions
    conditions = [
        Invoice.workspace_id == workspace_id,
        Invoice.created_at >= date_from,
        Invoice.created_at <= date_to
    ]
    
    if client_id:
        conditions.append(Invoice.client_id == client_id)
    
    # Add custom filters if provided
    if filters and "status" in filters:
        conditions.append(Invoice.status == filters["status"])
    
    # Get total revenue (sum of paid invoices)
    total_revenue = (
        await session.exec(
            select(func.sum(Invoice.amount))
            .where(
                *conditions,
                Invoice.status == "paid"
            )
        )
    ).one() or 0
    
    # Get invoice counts by status
    invoice_counts = {}
    for status in ["draft", "sent", "paid", "overdue"]:
        count = (
            await session.exec(
                select(func.count())
                .where(
                    *conditions,
                    Invoice.status == status
                )
            )
        ).one()
        invoice_counts[status] = count
    
    # Get opportunity data
    opp_conditions = [
        Opportunity.workspace_id == workspace_id,
        Opportunity.created_at >= date_from,
        Opportunity.created_at <= date_to
    ]
    
    if client_id:
        opp_conditions.append(Opportunity.client_id == client_id)
    
    # Get opportunity counts by status
    opportunity_counts = {}
    for status in ["new", "qualified", "proposal", "negotiation", "won", "lost"]:
        count = (
            await session.exec(
                select(func.count())
                .where(
                    *opp_conditions,
                    Opportunity.status == status
                )
            )
        ).one()
        opportunity_counts[status] = count
    
    # Calculate win rate
    total_closed = opportunity_counts.get("won", 0) + opportunity_counts.get("lost", 0)
    win_rate = (opportunity_counts.get("won", 0) / total_closed * 100) if total_closed > 0 else 0
    
    # Calculate average deal size
    avg_deal_size = (
        await session.exec(
            select(func.avg(Opportunity.value))
            .where(
                *opp_conditions,
                Opportunity.status == "won"
            )
        )
    ).one() or 0
    
    # Return compiled report data
    return {
        "report_type": "sales_overview",
        "time_period": {
            "start_date": date_from.isoformat(),
            "end_date": date_to.isoformat()
        },
        "metrics": {
            "total_revenue": total_revenue,
            "total_invoices": sum(invoice_counts.values()),
            "invoices_by_status": invoice_counts,
            "average_deal_size": avg_deal_size,
            "win_rate": win_rate,
            "total_opportunities": sum(opportunity_counts.values()),
            "opportunities_by_status": opportunity_counts
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

# Placeholder functions for other report types - to be implemented
async def generate_client_activity(session, workspace_id, date_from, date_to, client_id=None, filters=None):
    """Generate client activity report."""
    # Implementation will be added
    return {"status": "not_implemented", "report_type": "client_activity"}

async def generate_opportunity_pipeline(session, workspace_id, date_from, date_to, client_id=None, filters=None):
    """Generate opportunity pipeline report."""
    # Implementation will be added
    return {"status": "not_implemented", "report_type": "opportunity_pipeline"}

async def generate_invoice_aging(session, workspace_id, date_from, date_to, client_id=None, filters=None):
    """Generate invoice aging report."""
    # Implementation will be added
    return {"status": "not_implemented", "report_type": "invoice_aging"}

async def generate_task_completion(session, workspace_id, date_from, date_to, client_id=None, filters=None):
    """Generate task completion report."""
    # Implementation will be added
    return {"status": "not_implemented", "report_type": "task_completion"}

async def generate_revenue_forecast(session, workspace_id, date_from, date_to, client_id=None, filters=None):
    """Generate revenue forecast report."""
    # Implementation will be added
    return {"status": "not_implemented", "report_type": "revenue_forecast"}

async def generate_custom_report(session, workspace_id, date_from, date_to, metrics, dimensions, client_id=None, filters=None):
    """Generate custom report based on specified metrics and dimensions."""
    # Implementation will be added
    return {
        "status": "not_implemented", 
        "report_type": "custom",
        "metrics": metrics,
        "dimensions": dimensions
    }

def export_report_data(data, format, filename):
    """Export report data in the specified format."""
    if format == ExportFormat.JSON:
        return Response(
            content=json.dumps(data, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}.json"}
        )
    elif format == ExportFormat.CSV:
        # Flatten the data structure for CSV
        flattened_data = flatten_data(data)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=flattened_data[0].keys() if flattened_data else [])
        writer.writeheader()
        writer.writerows(flattened_data)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
        )
    elif format == ExportFormat.EXCEL:
        # For Excel export, we'll need to add pandas and openpyxl dependencies
        # This is a placeholder for now
        return Response(
            content=json.dumps({"error": "Excel export not implemented yet"}, default=str),
            media_type="application/json"
        )

def flatten_data(data, parent_key='', sep='_'):
    """Flatten nested dictionaries for CSV export."""
    items = []
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                items.extend(flatten_data(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    elif isinstance(data, list):
        # If it's a list of dictionaries, flatten each one
        flattened_list = []
        for item in data:
            if isinstance(item, dict):
                flattened_list.append(flatten_data(item))
        return flattened_list
    else:
        # If data is neither dict nor list, return it wrapped in a list
        return [{"value": data}]
