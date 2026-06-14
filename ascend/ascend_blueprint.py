"""
ascend Flask Blueprint
─────────────────────────
Registers all ascend routes under /ascend/ prefix.
This blueprint is registered in app.py only when ASCEND_ENABLED = True.

Routes:
  GET  /ascend/dashboard                 — ascend overview + risk forecast
  GET  /ascend/whatif                    — What-If sandbox page
  POST /ascend/whatif/simulate           — AJAX sandbox recalculation
  POST /ascend/feedback/<message_id>     — Store Helpful/False Alarm feedback
  GET  /ascend/feedback/suggestions      — View weight adjustment suggestions
  GET  /ascend/incident/<message_id>     — View incident report
  GET  /ascend/incident/<message_id>/export — Export incident report as text
"""

import json
from flask import Blueprint, render_template, request, jsonify, Response

import config
import database

# ─── Fail-safe imports for each ascend module ─────────────────────────────

try:
    from ascend import counterfactual
    COUNTERFACTUAL_OK = True
except Exception:
    COUNTERFACTUAL_OK = False

try:
    from ascend import threat_ontology
    ONTOLOGY_OK = True
except Exception:
    ONTOLOGY_OK = False

try:
    from ascend import risk_forecast
    FORECAST_OK = True
except Exception:
    FORECAST_OK = False

try:
    from ascend import psych_analyzer
    PSYCH_OK = True
except Exception:
    PSYCH_OK = False

try:
    from ascend import rule_feedback
    RULE_FEEDBACK_OK = True
except Exception:
    RULE_FEEDBACK_OK = False

try:
    from ascend import incident_reporter
    INCIDENT_OK = True
except Exception:
    INCIDENT_OK = False

try:
    from ascend import whatif_sandbox
    WHATIF_OK = True
except Exception:
    WHATIF_OK = False


# ─── Blueprint Definition ────────────────────────────────────────────────────

ascend_bp = Blueprint("ascend", __name__, url_prefix="/ascend")


# ─── Dashboard ────────────────────────────────────────────────────────────────

@ascend_bp.route("/dashboard")
def dashboard():
    """ascend overview page with risk forecast and feedback suggestions."""
    # Risk Forecast
    forecast_data = {}
    if FORECAST_OK:
        try:
            history = database.get_history(limit=50)
            forecast_data = risk_forecast.compute_risk_forecast(history)
        except Exception:
            pass

    # Feedback Suggestions
    feedback_suggestions = {}
    if RULE_FEEDBACK_OK:
        try:
            feedback_suggestions = rule_feedback.compute_weight_suggestions()
        except Exception:
            pass

    return render_template(
        "ascend_dashboard.html",
        forecast=forecast_data,
        feedback_suggestions=feedback_suggestions,
        module_status={
            "counterfactual": COUNTERFACTUAL_OK,
            "threat_ontology": ONTOLOGY_OK,
            "risk_forecast": FORECAST_OK,
            "psych_analyzer": PSYCH_OK,
            "rule_feedback": RULE_FEEDBACK_OK,
            "incident_reporter": INCIDENT_OK,
            "whatif_sandbox": WHATIF_OK,
        },
    )


# ─── What-If Sandbox ─────────────────────────────────────────────────────────

@ascend_bp.route("/whatif")
def whatif_page():
    """What-If sandbox page with weight sliders."""
    # Get recent analyses for the dropdown
    recent = []
    try:
        history = database.get_history(limit=20)
        for h in history:
            recent.append({
                "id": h.get("id"),
                "message_id": h.get("message_id", ""),
                "subject": h.get("subject", "Unknown"),
                "risk_score": h.get("risk_score", 0),
                "risk_level": h.get("risk_level", "Unknown"),
            })
    except Exception:
        pass

    return render_template(
        "whatif.html",
        recent_analyses=recent,
        default_weights=config.SCORE_WEIGHTS,
    )


@ascend_bp.route("/whatif/simulate", methods=["POST"])
def whatif_simulate():
    """AJAX endpoint: recalculate risk with custom weights."""
    if not WHATIF_OK:
        return jsonify({"error": "What-If module not available"}), 503

    try:
        data = request.get_json()
        log_id = data.get("log_id")
        custom_weights = data.get("weights", {})

        # Retrieve findings from analysis history
        log = database.get_log_by_id(int(log_id))
        if not log:
            return jsonify({"error": "Analysis not found"}), 404

        findings = json.loads(log.get("findings", "[]"))

        result = whatif_sandbox.simulate_risk_score(
            findings=findings,
            custom_weights=custom_weights,
            default_weights=config.SCORE_WEIGHTS,
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Rule Feedback ────────────────────────────────────────────────────────────

@ascend_bp.route("/feedback/<message_id>", methods=["POST"])
def submit_feedback(message_id):
    """Store Helpful / False Alarm feedback."""
    if not RULE_FEEDBACK_OK:
        return jsonify({"error": "Feedback module not available"}), 503

    try:
        data = request.get_json()
        feedback_type = data.get("feedback_type")
        risk_score = data.get("risk_score")
        risk_level = data.get("risk_level")
        triggered_rules = data.get("triggered_rules", [])

        if feedback_type not in ("helpful", "false_alarm"):
            return jsonify({"error": "Invalid feedback type"}), 400

        rule_feedback.submit_rule_feedback(
            message_id=message_id,
            feedback_type=feedback_type,
            risk_score=risk_score,
            risk_level=risk_level,
            triggered_rules=triggered_rules,
        )
        return jsonify({
            "success": True,
            "message": f"Feedback recorded: {feedback_type.replace('_', ' ').title()}",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ascend_bp.route("/feedback/status/<message_id>")
def feedback_status(message_id):
    """Check if ascend feedback exists for a message."""
    if not RULE_FEEDBACK_OK:
        return jsonify({"feedback": None})

    try:
        fb = rule_feedback.get_rule_feedback(message_id)
        return jsonify({"feedback": fb})
    except Exception:
        return jsonify({"feedback": None})


@ascend_bp.route("/feedback/suggestions")
def feedback_suggestions():
    """View weight adjustment suggestions."""
    if not RULE_FEEDBACK_OK:
        return jsonify({"error": "Feedback module not available"}), 503

    try:
        suggestions = rule_feedback.compute_weight_suggestions()
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Incident Reporter ───────────────────────────────────────────────────────

@ascend_bp.route("/incident/<message_id>")
def incident_report(message_id):
    """View an incident report for a specific analysis."""
    if not INCIDENT_OK:
        return render_template("incident_report.html", report=None,
                               error="Incident reporter not available.")

    try:
        # Retrieve analysis log
        conn = database.get_connection()
        row = conn.execute(
            "SELECT * FROM analysis_logs WHERE message_id = ? ORDER BY id DESC LIMIT 1",
            (message_id,),
        ).fetchone()
        conn.close()

        if not row:
            return render_template("incident_report.html", report=None,
                                   error="No analysis found for this email.")

        log = dict(row)
        findings = json.loads(log.get("findings", "[]"))
        risk_score = log.get("risk_score", 0)
        risk_level = log.get("risk_level", "Unknown")

        if not incident_reporter.should_generate_report(risk_score):
            return render_template(
                "incident_report.html", report=None,
                error=f"Risk score ({risk_score:.0f}) is below the incident threshold "
                      f"({incident_reporter.ascend_config.INCIDENT_THRESHOLD})."
            )

        # Generate ontology data if available
        ontology_data = []
        if ONTOLOGY_OK:
            try:
                ontology_data = threat_ontology.build_ontology(findings)
            except Exception:
                pass

        email_meta = {
            "id": message_id,
            "subject": log.get("subject", ""),
            "sender": log.get("sender", ""),
            "date": log.get("timestamp", ""),
        }

        report = incident_reporter.generate_incident_report(
            email_meta=email_meta,
            risk_score=risk_score,
            risk_level=risk_level,
            intent=log.get("intent", "Unknown"),
            findings=findings,
            ontology_data=ontology_data,
            summary=log.get("summary", ""),
        )

        return render_template("incident_report.html", report=report, error=None)

    except Exception as e:
        return render_template("incident_report.html", report=None,
                               error=f"Failed to generate report: {str(e)}")


@ascend_bp.route("/incident/<message_id>/export")
def incident_export(message_id):
    """Export incident report as plain text."""
    if not INCIDENT_OK:
        return jsonify({"error": "Incident reporter not available"}), 503

    try:
        conn = database.get_connection()
        row = conn.execute(
            "SELECT * FROM analysis_logs WHERE message_id = ? ORDER BY id DESC LIMIT 1",
            (message_id,),
        ).fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "No analysis found"}), 404

        log = dict(row)
        findings = json.loads(log.get("findings", "[]"))

        ontology_data = []
        if ONTOLOGY_OK:
            try:
                ontology_data = threat_ontology.build_ontology(findings)
            except Exception:
                pass

        email_meta = {
            "id": message_id,
            "subject": log.get("subject", ""),
            "sender": log.get("sender", ""),
            "date": log.get("timestamp", ""),
        }

        report = incident_reporter.generate_incident_report(
            email_meta=email_meta,
            risk_score=log.get("risk_score", 0),
            risk_level=log.get("risk_level", "Unknown"),
            intent=log.get("intent", "Unknown"),
            findings=findings,
            ontology_data=ontology_data,
            summary=log.get("summary", ""),
        )

        text_content = incident_reporter.export_as_text(report)
        return Response(
            text_content,
            mimetype="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=incident_{message_id[:8]}.txt"
            },
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
