from flask import Flask, render_template, redirect, url_for, request

from store.inmemory import InMemoryStore
from rules.rules_engine import RulesEngine
from state_machine.case_state_machine import CaseStateMachine
from services.clock import Clock
from services.email_ingestion_service import EmailIngestionService

from portals.attention import AttentionPortal
from portals.classification import ClassificationPortal
from portals.billing import BillingPortal

from simulators.email_simulator import EmailSimulator
from model.enums import CaseEventType

app = Flask(__name__)

# ---------------------------------
# BOOTSTRAP
# ---------------------------------

clock = Clock()
store = InMemoryStore()
rules = RulesEngine(store, CaseStateMachine())
ingestion = EmailIngestionService(store, rules, clock)

attention_portal = AttentionPortal()
classification_portal = ClassificationPortal()
billing_portal = BillingPortal()

email_simulator = EmailSimulator(ingestion, clock)

# ---------------------------------
# DASHBOARD V2
# ---------------------------------

@app.route("/")
def dashboard():
    now = clock.now()

    cases = store.list_cases()

    selected_case_id = request.args.get("case")
    selected_case = store.get_case(selected_case_id) if selected_case_id else None

    attention = attention_portal.collect(store, now)
    billing = billing_portal.collect(store, now)
    classifications = classification_portal.collect(
        ingestion.pending_classifications, now
    )

    attention_case_ids = {item.case_id for item in attention}

    return render_template(
        "dashboard_v2.html",
        cases=cases,
        selected_case=selected_case,
        attention=attention,
        billing=billing,
        classifications=classifications,
        attention_case_ids=attention_case_ids,
    )

# ---------------------------------
# SIMULAÇÃO
# ---------------------------------

@app.route("/sim/email/inbound")
def sim_email_inbound():
    email_simulator.receive_email(
        from_address="cliente@empresa.com",
        subject="Pedido de esclarecimento contratual",
        body="Pode confirmar este ponto?",
    )
    return redirect(url_for("dashboard"))

@app.route("/sim/time/<int:days>")
def sim_time(days):
    email_simulator.advance_days(days)
    now = clock.now()

    for case in store.list_cases():
        rules.handle_event(
            case=case,
            event_type=CaseEventType.TIME_PASSED,
            event_context={"days": days},
            now=now,
        )

    return redirect(url_for("dashboard"))

@app.route("/sim/email/outbound/<case_id>")
def sim_email_outbound(case_id):
    email_simulator.send_email(
        case_id=case_id,
        to_address="cliente@empresa.com",
        subject="Re: esclarecimento",
        body="Segue resposta ao seu pedido.",
    )
    return redirect(url_for("dashboard", case=case_id))

# ---------------------------------
# DECISÕES
# ---------------------------------

@app.route("/decision", methods=["POST"])
def decision():
    portal = request.form["portal"]
    action = request.form["action"]
    case_id = request.form.get("case_id")

    now = clock.now()

    if portal == "billing" and case_id:
        rules.handle_event(
            case=store.get_case(case_id),
            event_type=CaseEventType.USER_ACTION,
            event_context={"decision": action},
            now=now,
        )

    if portal == "classification":
        ingestion.pending_classifications.clear()

    return redirect(url_for("dashboard", case=case_id))

# ---------------------------------

if __name__ == "__main__":
    app.run(debug=True)
