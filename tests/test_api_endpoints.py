"""
REST API Endpoint Comprehensive Integration Tests
"""
from fastapi import status

def test_root_endpoint(client):
    """GET / returns system status and metadata."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "PostgreSQL" in data["database"]

def test_healthcheck_endpoint(client):
    """GET /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"

def test_departments_list(client, auth_headers):
    """GET /api/v1/departments/ returns active departments."""
    response = client.get("/api/v1/departments/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_organizational_chart_recursive_cte(client, auth_headers):
    """GET /api/v1/employees/org-chart/tree executes recursive CTE successfully."""
    response = client.get("/api/v1/employees/org-chart/tree", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_inventory_warehouses_list(client, auth_headers):
    """GET /api/v1/inventory/warehouses returns registered warehouses."""
    response = client.get("/api/v1/inventory/warehouses", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_accounts_receivable_aging_view(client, auth_headers):
    """GET /api/v1/billing/aging-report returns view data."""
    response = client.get("/api/v1/billing/aging-report", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_analytics_overview_kpis(client, auth_headers):
    """GET /api/v1/analytics/overview returns executive metrics and materialized views."""
    response = client.get("/api/v1/analytics/overview", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "kpis" in data
    assert "monthly_trends" in data
    assert "department_metrics" in data
    assert "top_projects" in data

def test_interactive_advanced_query_execution(client, auth_headers):
    """GET /api/v1/analytics/execute-query/1 executes SQL Query Q01 dynamically."""
    response = client.get("/api/v1/analytics/execute-query/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["query_number"] == 1
    assert "columns" in data
    assert "data" in data
