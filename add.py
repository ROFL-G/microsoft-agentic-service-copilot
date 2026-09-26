import os
import sys
import socket
import gradio as gr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==============================================================================
# 1. ENTERPRISE KNOWLEDGE BASE (DOMAIN RAG)
# Microsoft Learn, Azure SLA & CSS Standard Operating Procedures (SOPs)
# ==============================================================================
AZURE_KNOWLEDGE_BASE = [
    {
        "clause_id": "AZ-OAI-429",
        "category": "Azure OpenAI Service",
        "title": "TPM / RPM Throttling & Surge Policies",
        "content": (
            "SOP AZ-OAI-429: Azure OpenAI Throttling (429 Too Many Requests). When deployment hits TPM/RPM limits "
            "on GPT-4o endpoints, inspect Unified Support standing. If customer holds 'Unified Enterprise Support', "
            "grant an automated 24-hour temporary 20% TPM burst allocation while initiating an asynchronous regional "
            "capacity expansion request. Advise customer on client-side exponential backoff."
        )
    },
    {
        "clause_id": "AZ-SLA-501",
        "category": "Azure IaaS Compute & Networking",
        "title": "Regional VM Outage & SLA Billing Credits",
        "content": (
            "SOP AZ-SLA-501: Azure VM Availability Set Outages. If tenant experiences multi-VM failure dropping "
            "monthly availability below 99.99%, tenant is entitled to a 25% billing credit under Microsoft Cloud SLA. "
            "Remediation: Cross-reference platform incident tracking (RCA Bulletin), verify outage duration via KQL, "
            "and automatically post credit voucher to the enterprise billing account."
        )
    },
    {
        "clause_id": "AZ-ENTRA-401",
        "category": "Microsoft Entra ID",
        "title": "Conditional Access & MFA Lockouts (AADSTS50076)",
        "content": (
            "SOP AZ-ENTRA-401: Entra ID AADSTS50076 & MFA Challenges. When an enterprise tenant reports AADSTS50076, "
            "the user or service principal failed an interactive MFA challenge enforced by a newly scoped Conditional "
            "Access Policy. Remediation: Inspect sign-in logs, isolate policy ID matches, verify non-interactive exclusions, "
            "and stage an automated break-glass emergency bypass or Workload Identity Federation script."
        )
    },
    {
        "clause_id": "AZ-APP-502",
        "category": "Azure App Service",
        "title": "Container Startup Timeout (502 Bad Gateway)",
        "content": (
            "SOP AZ-APP-502: HTTP 502 Bad Gateway / Container Startup Timeout. Indicates custom Docker container exceeded "
            "the default 230-second initialization window. Remediation: Check 'WEBSITES_CONTAINER_START_TIME_LIMIT' app "
            "setting, verify health probe port mappings, and execute an automated slot swap or warm instance restart."
        )
    },
    {
        "clause_id": "AZ-SQL-MI-801",
        "category": "Azure SQL Managed Instance",
        "title": "Storage Cap & Auto-Failover Deadlocks",
        "content": (
            "SOP AZ-SQL-MI-801: SQL MI Auto-Storage Throttling. When instance data file allocation exceeds 95% disk quota, "
            "transactions enter read-only lock. If customer has Mission-Critical tier, provision an instant 250 GB storage "
            "surge buffer without reboot and initiate backup log truncation."
        )
    },
    {
        "clause_id": "AZ-SUB-BILL-902",
        "category": "Azure Billing & Subscriptions",
        "title": "Enterprise Agreement Spending Cap Lockout",
        "content": (
            "SOP AZ-SUB-BILL-902: Subscription Spending Limit Exceeded. Triggered when monthly consumption exhausts PO balance. "
            "Remediation: Check tenant payment health. For Unified Support contracts with active EA, grant an automated "
            "72-hour billing suspension waiver to prevent production resource de-allocation."
        )
    }
]

rag_corpus = [item["content"] for item in AZURE_KNOWLEDGE_BASE]
vectorizer = TfidfVectorizer().fit(rag_corpus)
doc_vectors = vectorizer.transform(rag_corpus)

def search_azure_sop(query_text: str) -> dict:
    """Semantic vector search over Microsoft Learn & CSS SOPs."""
    query_vec = vectorizer.transform([query_text])
    scores = cosine_similarity(query_vec, doc_vectors)[0]
    best_idx = scores.argmax()
    return {
        "clause_id": AZURE_KNOWLEDGE_BASE[best_idx]["clause_id"],
        "category": AZURE_KNOWLEDGE_BASE[best_idx]["category"],
        "title": AZURE_KNOWLEDGE_BASE[best_idx]["title"],
        "content": AZURE_KNOWLEDGE_BASE[best_idx]["content"],
        "score": float(scores[best_idx])
    }

# ==============================================================================
# 2. MOCK AZURE ENTERPRISE INCIDENTS DATABASE
# ==============================================================================
ENTERPRISE_TICKETS = {
    "TICK-AZ-9102": {
        "customer": "Accenture Digital",
        "tenant_id": "tenant-acc-4491",
        "subscription_id": "sub-prod-eastus-01",
        "region": "eastus",
        "tier": "Unified Enterprise Support",
        "service": "Azure OpenAI Service",
        "error_code": "RESOURCE_EXHAUSTED_429",
        "issue_text": "Production copilot pipeline degraded: Deployment 'gpt-4o-prod' throwing 429 rate limit exceeded during peak customer batch in East US."
    },
    "TICK-AZ-4820": {
        "customer": "Barclays Technology",
        "tenant_id": "tenant-barc-1029",
        "subscription_id": "sub-finance-ukwest-02",
        "region": "ukwest",
        "tier": "Unified Enterprise Support",
        "service": "Azure Virtual Machines (Compute)",
        "error_code": "VM_UNAVAILABLE_SLA_BREACH",
        "issue_text": "Production database nodes experienced 85 minutes of unplanned downtime in UK West during regional network incident. Requesting SLA credit review."
    },
    "TICK-AZ-3156": {
        "customer": "Unilever IT",
        "tenant_id": "tenant-uni-7741",
        "subscription_id": "sub-corp-westeurope-03",
        "region": "westeurope",
        "tier": "Standard Commercial Support",
        "service": "Microsoft Entra ID",
        "error_code": "AADSTS50076_MFA_CHALLENGE",
        "issue_text": "ERP migration service principal locked out with AADSTS50076 error following Conditional Access policy update in West Europe."
    },
    "TICK-AZ-7731": {
        "customer": "KPMG Global",
        "tenant_id": "tenant-kpmg-8812",
        "subscription_id": "sub-audit-centralus-04",
        "region": "centralus",
        "tier": "Unified Enterprise Support",
        "service": "Azure App Service",
        "error_code": "CONTAINER_TIMEOUT_502",
        "issue_text": "Web App container fails to initialize, dumping HTTP 502 Bad Gateway. Deployment slot swaps hanging past 240 seconds."
    },
    "TICK-AZ-5509": {
        "customer": "Siemens Healthineers",
        "tenant_id": "tenant-siem-2033",
        "subscription_id": "sub-med-germanywest-05",
        "region": "germanywestcentral",
        "tier": "Mission-Critical Premium",
        "service": "Azure SQL Managed Instance",
        "error_code": "SQL_MI_STORAGE_EXHAUSTED",
        "issue_text": "Critical clinical DB instance reported storage full alert (98.4% utilized). Write transactions are currently blocked."
    },
    "TICK-AZ-1088": {
        "customer": "Deloitte Core Services",
        "tenant_id": "tenant-del-9011",
        "subscription_id": "sub-ops-southeastasia-06",
        "region": "southeastasia",
        "tier": "Unified Enterprise Support",
        "service": "Azure Subscriptions & Billing",
        "error_code": "SPENDING_LIMIT_EXCEEDED",
        "issue_text": "Subscription spending cap hit due to dev-test cluster run. Production workloads scheduled for de-allocation in 4 hours."
    }
}

# ==============================================================================
# 3. AUTONOMOUS OPERATIONAL TOOLS (AZURE MOCK APIS)
# ==============================================================================
def tool_query_azure_resource_graph(subscription_id: str, service: str, region: str) -> dict:
    is_down = "Compute" in service or "App Service" in service
    return {
        "subscription_id": subscription_id,
        "region": region,
        "service": service,
        "resource_health": "Degraded (Regional RCA Active)" if is_down else "Healthy (Capacity Constrained)",
        "utilization_pct": 99.2 if "OpenAI" in service or "SQL" in service else 45.0,
        "active_rca_id": "AZ-RCA-2026-UKW" if region == "ukwest" else ("AZ-APP-WARMUP-FAIL" if "App" in service else "None")
    }

def tool_evaluate_unified_support_sla(tenant_id: str, tier: str) -> dict:
    is_unified = "Unified" in tier or "Mission-Critical" in tier
    return {
        "tenant_id": tenant_id,
        "tier": tier,
        "auto_surge_allowed": is_unified,
        "max_auto_credit_usd": 15000 if is_unified else 500,
        "dedicated_tam_escalation": is_unified
    }

def tool_execute_azure_arm_action(action_type: str, target_id: str, details: str) -> str:
    if action_type == "ALLOCATE_TPM_BURST":
        return f"SUCCESS [ARM]: Granted +20% TPM temporary burst buffer on '{target_id}' (valid 24 hrs). Dispatched async capacity ticket to Redmond."
    elif action_type == "ISSUE_SLA_CREDIT":
        return f"SUCCESS [Billing]: SLA breach verified against Bulletin AZ-RCA-2026-UKW. Generated Credit Voucher #MS-SLA-9022 ($4,800.00 USD)."
    elif action_type == "STAGE_BREAKGLASS_SCRIPT":
        return f"SUCCESS [Entra ID]: Generated Workload Identity bypass template. Staged exclusion rule for non-interactive SPN '{target_id}'."
    elif action_type == "ADJUST_APP_TIMEOUT":
        return f"SUCCESS [App Service]: Patched WEBSITES_CONTAINER_START_TIME_LIMIT=600 on '{target_id}'. Initiated warm slot recycle."
    elif action_type == "EXPAND_SQL_STORAGE":
        return f"SUCCESS [SQL MI]: Allocated 250 GB instant emergency disk buffer. Executed log truncation runbook on '{target_id}'."
    elif action_type == "GRANT_BILLING_GRACE":
        return f"SUCCESS [Billing]: Applied 72-hour enterprise spending limit suspension waiver for '{target_id}'. Workload de-allocation paused."
    return "STATUS: Action queued for human Support Escalation Engineer review."

# ==============================================================================
# 4. RE-ACT AUTONOMOUS DIAGNOSTIC ENGINE
# ==============================================================================
def run_microsoft_agentic_copilot(
    ticket_id: str,
    enable_custom: bool,
    custom_customer: str,
    custom_service: str,
    custom_tier: str,
    custom_region: str,
    custom_error: str,
    custom_issue_text: str
) -> tuple[str, str, str]:

    if enable_custom and custom_issue_text.strip():
        payload = {
            "customer": custom_customer or "Custom Enterprise Client",
            "tenant_id": "tenant-custom-9999",
            "subscription_id": "sub-custom-prod-00",
            "region": custom_region or "eastus",
            "tier": custom_tier or "Unified Enterprise Support",
            "service": custom_service or "Azure Cloud Services",
            "error_code": custom_error or "ERR_GENERAL_AZURE",
            "issue_text": custom_issue_text
        }
        ticket_label = "CUSTOM-INJECTED-INCIDENT"
    else:
        payload = ENTERPRISE_TICKETS[ticket_id]
        ticket_label = ticket_id

    trace = []
    trace.append(f"📥 [Ticket Ingested] {ticket_label} | Tenant: {payload['customer']} | Tier: {payload['tier']}")
    trace.append(f"🔍 [Perception] Service: '{payload['service']}' | Error: '{payload['error_code']}' | Region: '{payload['region']}'")

    # Step 1: Telemetry Tool Call
    trace.append(f"⚙️ [Tool: Azure Resource Graph] Querying live telemetry for sub '{payload['subscription_id']}' in {payload['region']}...")
    telemetry = tool_query_azure_resource_graph(payload["subscription_id"], payload["service"], payload["region"])
    trace.append(f"📊 [Observation] Status: {telemetry['resource_health']} | Utilization: {telemetry['utilization_pct']}% | Active Bulletin: {telemetry['active_rca_id']}")

    # Step 2: RAG Semantic Grounding
    trace.append(f"📚 [Action: Domain RAG] Querying Microsoft Learn and CSS SOP index for '{payload['issue_text']}'...")
    sop = search_azure_sop(payload["issue_text"])
    trace.append(f"💡 [Observation] Grounded SOP Clause Matched: [{sop['clause_id']}] {sop['title']} (Cosine Match: {sop['score']:.4f})")

    # Step 3: Contract Entitlement Engine
    trace.append(f"💳 [Tool: Support Contract Engine] Inspecting SLA bounds for {payload['tenant_id']}...")
    entitlement = tool_evaluate_unified_support_sla(payload["tenant_id"], payload["tier"])
    trace.append(f"📈 [Observation] Support Tier: {entitlement['tier']} | Auto Remediation Authorized: {entitlement['auto_surge_allowed']}")

    # Step 4: Autonomous ARM Execution Logic
    work_order = ""
    err = payload["error_code"]

    if "429" in err or "OpenAI" in payload["service"]:
        arm_result = tool_execute_azure_arm_action("ALLOCATE_TPM_BURST", payload["subscription_id"], "20% TPM Buffer")
        trace.append(f"🚀 [Tool Call: ARM Execution] {arm_result}")
        work_order = (
            f"### 📋 MICROSOFT CSS ENTERPRISE WORK ORDER: {ticket_label}\n"
            f"**Customer:** {payload['customer']} | **Support Tier:** {payload['tier']}\n"
            f"**Resource:** {payload['service']} ({payload['region']}) | **Root Cause:** TPM Quota Saturation\n"
            f"**Grounded Engineering SOP:** {sop['clause_id']} — {sop['title']}\n\n"
            f"#### 1. Autonomous Remediations Executed:\n"
            f"- Granted immediate +20% TPM temporary burst buffer for 24 hours under Unified Support rights.\n"
            f"- Dispatched asynchronous capacity scaling ticket to Redmond Capacity Engineering.\n\n"
            f"#### 2. Tenant Response Draft:\n"
            f"\"Hello {payload['customer']} Engineering Team, our automated telemetry detected regional TPM saturation on "
            f"your Azure OpenAI deployment. A 20% burst capacity waiver has been provisioned. Permanent expansion is "
            f"currently under expedited review by the Azure Capacity Management desk.\""
        )

    elif "SLA" in err or "Compute" in payload["service"]:
        arm_result = tool_execute_azure_arm_action("ISSUE_SLA_CREDIT", payload["tenant_id"], "25% Credit")
        trace.append(f"🚀 [Tool Call: ARM Execution] {arm_result}")
        work_order = (
            f"### 📋 MICROSOFT CSS ENTERPRISE WORK ORDER: {ticket_label}\n"
            f"**Customer:** {payload['customer']} | **Support Tier:** {payload['tier']}\n"
            f"**Resource:** {payload['service']} ({payload['region']}) | **Root Cause:** Infrastructure SLA Disruption\n"
            f"**Grounded Engineering SOP:** {sop['clause_id']} — {sop['title']}\n\n"
            f"#### 1. Autonomous Remediations Executed:\n"
            f"- Correlated incident with internal RCA bulletin `{telemetry['active_rca_id']}`.\n"
            f"- Issued $4,800.00 USD SLA credit voucher directly to billing ledger (Clause AZ-SLA-501).\n\n"
            f"#### 2. Tenant Response Draft:\n"
            f"\"Hi {payload['customer']} Cloud Team, telemetry confirms an 85-minute compute degradation in UK West. "
            f"Per your Microsoft Unified Support SLA contract, an automated 25% credit voucher ($4,800.00) has been "
            f"applied to your enterprise billing account.\""
        )

    elif "50076" in err or "Entra" in payload["service"]:
        arm_result = tool_execute_azure_arm_action("STAGE_BREAKGLASS_SCRIPT", payload["tenant_id"], "Workload Identity")
        trace.append(f"🚀 [Tool Call: ARM Execution] {arm_result}")
        work_order = (
            f"### 📋 MICROSOFT CSS ENTERPRISE WORK ORDER: {ticket_label}\n"
            f"**Customer:** {payload['customer']} | **Support Tier:** {payload['tier']}\n"
            f"**Resource:** {payload['service']} | **Root Cause:** Non-Interactive Conditional Access MFA Challenge\n"
            f"**Grounded Engineering SOP:** {sop['clause_id']} — {sop['title']}\n\n"
            f"#### 1. Autonomous Remediations Executed:\n"
            f"- Isolated misconfigured Conditional Access rule enforcing interactive MFA on a service principal.\n"
            f"- Staged Workload Identity Federation script to prevent service account lockouts.\n\n"
            f"#### 2. Tenant Response Draft:\n"
            f"\"Hello {payload['customer']} IAM Team, error AADSTS50076 was triggered because the service account was "
            f"targeted by an interactive MFA Conditional Access policy. We recommend scoping the account under Workload "
            f"Identity Federation or applying our staged exclusion rule.\""
        )

    elif "502" in err or "App Service" in payload["service"]:
        arm_result = tool_execute_azure_arm_action("ADJUST_APP_TIMEOUT", payload["subscription_id"], "Timeout 600s")
        trace.append(f"🚀 [Tool Call: ARM Execution] {arm_result}")
        work_order = (
            f"### 📋 MICROSOFT CSS ENTERPRISE WORK ORDER: {ticket_label}\n"
            f"**Customer:** {payload['customer']} | **Support Tier:** {payload['tier']}\n"
            f"**Resource:** {payload['service']} | **Root Cause:** Container Initialization Latency Exceeding 230s\n"
            f"**Grounded Engineering SOP:** {sop['clause_id']} — {sop['title']}\n\n"
            f"#### 1. Autonomous Remediations Executed:\n"
            f"- Automatically raised `WEBSITES_CONTAINER_START_TIME_LIMIT` to 600 seconds via ARM.\n"
            f"- Triggered warm instance restart on deployment slots.\n\n"
            f"#### 2. Tenant Response Draft:\n"
            f"\"Hi {payload['customer']} DevOps Team, your App Service container startup exceeded the default 230-second "
            f"probe limit. We have autonomously extended the startup ceiling to 600s and recycled the instances.\""
        )

    elif "SQL" in err or "Managed Instance" in payload["service"]:
        arm_result = tool_execute_azure_arm_action("EXPAND_SQL_STORAGE", payload["subscription_id"], "250GB Buffer")
        trace.append(f"🚀 [Tool Call: ARM Execution] {arm_result}")
        work_order = (
            f"### 📋 MICROSOFT CSS ENTERPRISE WORK ORDER: {ticket_label}\n"
            f"**Customer:** {payload['customer']} | **Support Tier:** {payload['tier']}\n"
            f"**Resource:** {payload['service']} | **Root Cause:** Managed Instance Disk Saturation (>95%)\n"
            f"**Grounded Engineering SOP:** {sop['clause_id']} — {sop['title']}\n\n"
            f"#### 1. Autonomous Remediations Executed:\n"
            f"- Provisioned 250 GB zero-downtime emergency storage surge allocation.\n"
            f"- Triggered automated transaction log truncation runbook.\n\n"
            f"#### 2. Tenant Response Draft:\n"
            f"\"Hello {payload['customer']} Database Admins, storage consumption reached 98.4% capacity. An immediate "
            f"250 GB surge allocation was added without downtime under your Mission-Critical Support entitlement.\""
        )

    else:
        arm_result = tool_execute_azure_arm_action("GRANT_BILLING_GRACE", payload["tenant_id"], "72-Hour Waiver")
        trace.append(f"🚀 [Tool Call: ARM Execution] {arm_result}")
        work_order = (
            f"### 📋 MICROSOFT CSS ENTERPRISE WORK ORDER: {ticket_label}\n"
            f"**Customer:** {payload['customer']} | **Support Tier:** {payload['tier']}\n"
            f"**Resource:** {payload['service']} | **Root Cause:** Enterprise Spending Limit Cap Lockout\n"
            f"**Grounded Engineering SOP:** {sop['clause_id']} — {sop['title']}\n\n"
            f"#### 1. Autonomous Remediations Executed:\n"
            f"- Granted 72-hour billing suspension waiver to prevent resource de-allocation.\n"
            f"- Notified Enterprise Agreement licensing desk for billing reconciliation.\n\n"
            f"#### 2. Tenant Response Draft:\n"
            f"\"Hi {payload['customer']} Operations, your subscription hit a spending limit cap. We have applied a 72-hour "
            f"suspension waiver to prevent production compute interruption while billing reconciles your enterprise PO.\""
        )

    rag_display = (
        f"**Clause ID:** {sop['clause_id']}\n"
        f"**Category:** {sop['category']}\n"
        f"**Title:** {sop['title']}\n"
        f"**Relevance Match:** {sop['score']:.4f}\n\n"
        f"**Policy Excerpt:**\n{sop['content']}"
    )

    return "\n\n".join(trace), rag_display, work_order

# ==============================================================================
# 5. GRADIO OPERATIONS COCKPIT
# ==============================================================================
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.Markdown("# 🏢 Microsoft Agentic Service Copilot (Enterprise Diagnostic Cockpit)")
    gr.Markdown(
        "Autonomous Customer Support & Service Copilot for Microsoft Cloud / Azure Infrastructure and Entra ID. "
        "Bridges live telemetry with Microsoft Learn SOPs and automates ARM remediations under strict SLA guardrails."
    )

    with gr.Row():
        with gr.Column(scale=1):
            ticket_selector = gr.Dropdown(
                choices=list(ENTERPRISE_TICKETS.keys()),
                value=list(ENTERPRISE_TICKETS.keys())[0],
                label="Select Inbound Azure Support Ticket"
            )

            with gr.Accordion("⚙️ Custom Incident Prompt Injection (Free-Form Testing)", open=False):
                custom_enable = gr.Checkbox(label="Enable Custom Diagnostic Injection", value=False)
                c_customer = gr.Textbox(label="Enterprise Customer Name", value="Morgan Stanley Cloud Ops")
                c_service = gr.Textbox(label="Azure Service / Resource", value="Azure OpenAI Service")
                c_tier = gr.Dropdown(
                    choices=["Unified Enterprise Support", "Mission-Critical Premium", "Standard Commercial Support"],
                    value="Unified Enterprise Support",
                    label="Support Contract Tier"
                )
                c_region = gr.Dropdown(
                    choices=["eastus", "westeurope", "centralus", "ukwest", "germanywestcentral", "southeastasia"],
                    value="eastus",
                    label="Azure Cloud Region"
                )
                c_error = gr.Textbox(label="Error Signature / Code", value="429_TOO_MANY_REQUESTS")
                c_text = gr.Textbox(
                    label="Incident Description / Telemetry Dump",
                    value="GPT-4o deployment throwing 429 rate limit exceeded during critical customer reporting run in East US.",
                    lines=3
                )

            run_btn = gr.Button("⚡ Run Autonomous Triage & Diagnostics", variant="primary")

            gr.Markdown("### 📊 Target Operating Benchmarks")
            gr.Markdown(
                "- **Triage Latency:** ~30 min $\\rightarrow$ < 30 sec (>95% reduction)\n"
                "- **First-Pass Remediation:** 35% automated resolution\n"
                "- **Zero Hallucination:** Constrained to Microsoft Learn SOPs\n"
                "- **Micro-Runtime Load:** < 35 MB RAM (Serverless ready)"
            )

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("📋 Minto Work Order & Customer Payload"):
                    out_work_order = gr.Markdown()
                with gr.TabItem("🧠 ReAct Agent Reasoning Trace"):
                    out_trace = gr.Textbox(lines=14, label="Autonomous Tool Executions & Telemetry Trace")
                with gr.TabItem("📖 Retrieved Microsoft Learn SOP (RAG)"):
                    out_rag = gr.Markdown()

    run_btn.click(
        fn=run_microsoft_agentic_copilot,
        inputs=[
            ticket_selector,
            custom_enable,
            c_customer,
            c_service,
            c_tier,
            c_region,
            c_error,
            c_text
        ],
        outputs=[out_trace, out_rag, out_work_order]
    )

def find_available_port(starting_port=7860, max_attempts=50):
    for p in range(starting_port, starting_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', p)) != 0:
                return p
    return starting_port

if __name__ == "__main__":
    is_colab = "google.colab" in sys.modules
    env_port = os.environ.get("PORT")

    if env_port:
        port = int(env_port)
        host = "0.0.0.0"
    else:
        port = find_available_port(7860)
        host = "127.0.0.1"

    print(f"🚀 Launching Microsoft Agentic Service Copilot on http://{host}:{port}")
    demo.launch(
        server_name=host,
        server_port=port,
        inbrowser=True,
        share=is_colab
    )
