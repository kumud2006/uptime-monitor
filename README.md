# uptime-monitor

A serverless website and API uptime monitor on Azure. It checks registered URLs every 5 minutes, records status and response time, tracks incidents, and emails you when a site goes down or recovers.

Live demo: https://calm-mud-09fd81f00.6.azurestaticapps.net

Dashboard

**Features**
Scheduled checks every 5 minutes, even when no browser is open

Incident tracking with one DOWN and one RECOVERED email per outage

React dashboard with status, response-time chart and incident log

SSRF protection: only public IPs allowed, no redirects

Terraform for infrastructure, GitHub Actions for CI/CD


**Tech Stack**

React + Vite, Python 3.11, Azure Functions, Cosmos DB, Azure Static Web Apps, Application Insights, Terraform, GitHub Actions
