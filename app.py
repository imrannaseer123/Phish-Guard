"""
Flask Web Application — Phishing Email Risk Analyzer
─────────────────────────────────────────────────────
Routes:
  /               Landing page
  /about          About page
  /auth           Initiates Gmail OAuth
  /oauth/callback OAuth callback handler
  /logout         Clear credentials
  /inbox          Shows inbox emails for selection
  /analyze/<id>   Runs analysis and shows explainability report
  /history        Past analysis log dashboard
  /feedback/<id>  Submit user feedback (Feature 3)
  /admin/weights  Adaptive weight suggestions (Feature 4)
  /dashboard      Weekly security summary (Feature 5)
  /campaigns      Cross-email campaign detection (Feature v2-3)
  /risk-profile   User risk exposure profile (Feature v2-6)
  /export/<id>    Forensic evidence export (Feature v2-8)
  /training       Security training simulation (Feature v2-10)
  /training/<id>  Training scenario evaluation (Feature v2-10)
"""

import os
import json
import re

from flask import (
    Flask, render_template, redirect, url_for,
    session, request, flash, jsonify,
)

import config
import gmail_auth
import gmail_reader
import database
from phishing_engine import EmailData, analyze_email
from risk_scorer import generate_report

# ─── Feature Module Imports (fail-safe) ───────────────────────────────────────
# Each import is wrapped so that a failure in any extension module
# does not prevent the core app from starting.

try:
    import sender_trust
    SENDER_TRUST_AVAILABLE = True
except Exception:
    SENDER_TRUST_AVAILABLE = False

try:
    import feedback as feedback_module
    FEEDBACK_AVAILABLE = True
except Exception:
    FEEDBACK_AVAILABLE = False

try:
    import weight_advisor
    WEIGHT_ADVISOR_AVAILABLE = True
except Exception:
    WEIGHT_ADVISOR_AVAILABLE = False

try:
    import weekly_summary
    WEEKLY_SUMMARY_AVAILABLE = True
except Exception:
    WEEKLY_SUMMARY_AVAILABLE = False

# ─── v2 Feature Module Imports (fail-safe) ────────────────────────────────────

try:
    import killchain
    KILLCHAIN_AVAILABLE = True
except Exception:
    KILLCHAIN_AVAILABLE = False

try:
    import linguistic_deception
    LINGUISTIC_AVAILABLE = True
except Exception:
    LINGUISTIC_AVAILABLE = False

try:
    import campaign_detector
    CAMPAIGN_AVAILABLE = True
except Exception:
    CAMPAIGN_AVAILABLE = False

try:
    import domain_heuristics
    DOMAIN_HEURISTICS_AVAILABLE = True
except Exception:
    DOMAIN_HEURISTICS_AVAILABLE = False

try:
    import safe_explainer
    SAFE_EXPLAINER_AVAILABLE = True
except Exception:
    SAFE_EXPLAINER_AVAILABLE = False

try:
    import risk_profile as risk_profile_module
    RISK_PROFILE_AVAILABLE = True
except Exception:
    RISK_PROFILE_AVAILABLE = False

try:
    from chatbot_blueprint import chatbot_bp
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    print("Warning: chatbot_blueprint or dependencies not found. Chatbot disabled.")



try:
    import severity_index
    SEVERITY_INDEX_AVAILABLE = True
except Exception:
    SEVERITY_INDEX_AVAILABLE = False

try:
    import forensic_export
    FORENSIC_AVAILABLE = True
except Exception:
    FORENSIC_AVAILABLE = False

try:
    import rule_confidence
    RULE_CONFIDENCE_AVAILABLE = True
except Exception:
    RULE_CONFIDENCE_AVAILABLE = False

try:
    import training_sim
    TRAINING_AVAILABLE = True
except Exception:
    TRAINING_AVAILABLE = False

try:
    import user_profile
    USER_PROFILE_AVAILABLE = True
except Exception:
    USER_PROFILE_AVAILABLE = False

try:
    import header_graph
    HEADER_GRAPH_AVAILABLE = True
except Exception:
    HEADER_GRAPH_AVAILABLE = False

# ─── ascend Framework Imports (fail-safe) ─────────────────────────────────

ASCEND_AVAILABLE = False
if config.ASCEND_ENABLED:
    try:
        from ascend.ascend_blueprint import ascend_bp
        from ascend import counterfactual as mn_counterfactual
        from ascend import threat_ontology as mn_ontology
        from ascend import psych_analyzer as mn_psych
        from ascend import incident_reporter as mn_incident
        from ascend import rule_feedback as mn_rule_feedback
        ASCEND_AVAILABLE = True
    except Exception as e:
        print(f"ascend framework failed to load: {e}")

# ─── App Setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Inject toggles into all templates
@app.context_processor
def inject_config():
    return {
        "ENABLE_CHATBOT": config.ENABLE_CHATBOT,
        "ASCEND_ENABLED": config.ASCEND_ENABLED and ASCEND_AVAILABLE,
    }



# Register Chatbot Blueprint
if config.ENABLE_CHATBOT and CHATBOT_AVAILABLE:
    try:
        app.register_blueprint(chatbot_bp)
    except Exception as e:
        print(f"Chatbot module failed to load: {e}")

# Register ascend Blueprint
if config.ASCEND_ENABLED and ASCEND_AVAILABLE:
    try:
        app.register_blueprint(ascend_bp)
    except Exception as e:
        print(f"ascend framework failed to register: {e}")

# Allow OAuth over HTTP for local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# ─── Core Routes (unchanged) ─────────────────────────────────────────────────

@app.route("/")
def index():
    """Landing page."""
    authenticated = gmail_auth.get_credentials() is not None
    return render_template("index.html", authenticated=authenticated)


@app.route("/about")
def about():
    """About page — project details, uses, and purposes."""
    return render_template("about.html")


@app.route("/auth")
def auth():
    """Initiate Gmail OAuth flow."""
    try:
        redirect_uri = url_for("oauth_callback", _external=True)
        flow = gmail_auth.get_flow(redirect_uri)
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        session["oauth_state"] = state
        return redirect(authorization_url)
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))


@app.route("/oauth/callback")
def oauth_callback():
    """Handle the OAuth callback from Google."""
    try:
        redirect_uri = url_for("oauth_callback", _external=True)
        flow = gmail_auth.get_flow(redirect_uri)
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        gmail_auth.save_credentials(creds)
        flash("✅ Gmail connected successfully!", "success")
        return redirect(url_for("inbox"))
    except Exception as e:
        flash(f"Authentication failed: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """Clear stored credentials."""
    gmail_auth.clear_credentials()
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


@app.route("/inbox")
def inbox():
    """Display inbox emails for selection."""
    creds = gmail_auth.get_credentials()
    if not creds:
        flash("Please connect your Gmail account first.", "warning")
        return redirect(url_for("index"))

    try:
        emails = gmail_reader.list_inbox(creds)
        return render_template("inbox.html", emails=emails)
    except Exception as e:
        flash(f"Failed to load inbox: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/email/content/<message_id>")
def email_content(message_id):
    """Return email body content as JSON for inline preview."""
    creds = gmail_auth.get_credentials()
    if not creds:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        msg = gmail_reader.get_message(creds, message_id)
        return jsonify({
            "success": True,
            "subject": msg.get("subject", ""),
            "sender": msg.get("sender", ""),
            "date": msg.get("date", ""),
            "body_html": msg.get("body_html", ""),
            "body_text": msg.get("body_text", ""),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze/<message_id>")
def analyze(message_id):
    """Analyze a specific email and show the explainability report."""
    creds = gmail_auth.get_credentials()
    if not creds:
        flash("Please connect your Gmail account first.", "warning")
        return redirect(url_for("index"))

    try:
        # Fetch full message
        msg = gmail_reader.get_message(creds, message_id)

        # Prepare email data for engine
        email_data = EmailData(
            subject=msg["subject"],
            sender_raw=msg["sender"],
            body_text=msg["body_text"],
            body_html=msg["body_html"],
            date=msg["date"],
            message_id=msg["id"],
        )

        # Run analysis
        findings = analyze_email(email_data)
        report = generate_report(findings)

        # Log to database
        findings_serialized = [
            {
                "analyzer": f.analyzer,
                "indicator": f.indicator,
                "score": f.score,
                "evidence": f.evidence,
                "explanation": f.explanation,
            }
            for f in report.findings
        ]
        database.log_analysis(
            message_id=message_id,
            sender=msg["sender"],
            subject=msg["subject"],
            risk_score=report.risk_score,
            risk_level=report.risk_level,
            intent=report.intent,
            findings_data=findings_serialized,
            summary=report.explanation_summary,
        )

        # Log to user risk profile (privacy-safe)
        try:
            database.log_risk_trend(report.risk_score, report.risk_level)
        except Exception:
            pass

        # Compute analyzer max scores for bar chart
        analyzer_max = config.SCORE_WEIGHTS

        # ── Feature 2: Sender Trust (fail-safe) ──
        trust_data = None
        if SENDER_TRUST_AVAILABLE:
            try:
                sender_trust.update_trust(msg["sender"], report.risk_level)
                domain = sender_trust._extract_domain(msg["sender"])
                trust_data = sender_trust.get_trust_recommendation(domain)
            except Exception:
                pass  # Fail silently — core report still renders

        # ── Feature 3: Existing Feedback (fail-safe) ──
        existing_feedback = None
        if FEEDBACK_AVAILABLE:
            try:
                existing_feedback = feedback_module.get_feedback(message_id)
            except Exception:
                pass

        # ── v2 Feature 1: Kill-Chain Mapping (fail-safe) ──
        killchain_data = None
        if KILLCHAIN_AVAILABLE:
            try:
                killchain_data = killchain.map_to_killchain(report.findings, report)
            except Exception:
                pass

        # ── v2 Feature 2: Linguistic Deception (fail-safe) ──
        linguistic_data = None
        if LINGUISTIC_AVAILABLE:
            try:
                linguistic_data = linguistic_deception.analyze_linguistic_deception(
                    msg.get("subject", ""), msg.get("body_text", "")
                )
            except Exception:
                pass

        # ── v2 Feature 3: Campaign Detection (fail-safe) ──
        campaign_data = None
        if CAMPAIGN_AVAILABLE:
            try:
                sender_domain_for_campaign = ""
                if "@" in msg.get("sender", ""):
                    sender_domain_for_campaign = msg["sender"].split("@")[-1].strip(">")
                campaign_detector.store_fingerprint(
                    message_id, msg.get("subject", ""),
                    msg.get("body_text", ""), sender_domain_for_campaign,
                    report.intent, report.risk_level,
                )
                campaign_data = campaign_detector.get_campaign_match(message_id)
            except Exception:
                pass

        # ── Header Route Graph (fail-safe) ──
        header_graph_data = None
        if config.HEADER_GRAPH_ENABLED and HEADER_GRAPH_AVAILABLE:
            try:
                header_graph_data = header_graph.build_graph_data(
                    msg.get("payload_headers", [])
                )
            except Exception:
                pass

        # ── v2 Feature 4: Domain Heuristics (fail-safe) ──
        domain_data = None
        if DOMAIN_HEURISTICS_AVAILABLE:
            try:
                sender_domain_for_heuristics = ""
                if "@" in msg.get("sender", ""):
                    sender_domain_for_heuristics = msg["sender"].split("@")[-1].strip(">")
                domain_data = domain_heuristics.analyze_domain(sender_domain_for_heuristics)
            except Exception:
                pass

        # ── v2 Feature 5: Safe Explainer (fail-safe) ──
        safe_data = None
        if SAFE_EXPLAINER_AVAILABLE:
            try:
                sender_domain_for_safe = ""
                if "@" in msg.get("sender", ""):
                    sender_domain_for_safe = msg["sender"].split("@")[-1].strip(">")
                safe_data = safe_explainer.explain_safe_classification(
                    report, sender_domain_for_safe
                )
            except Exception:
                pass

        # ── v2 Feature 7: Phishing Severity Index (fail-safe) ──
        psi_data = None
        if SEVERITY_INDEX_AVAILABLE:
            try:
                psi_data = severity_index.compute_psi(report)
            except Exception:
                pass

        # ── v2 Feature 9: Rule Confidence (fail-safe) ──
        confidence_data = None
        if RULE_CONFIDENCE_AVAILABLE:
            try:
                confidence_data = rule_confidence.compute_rule_confidence()
            except Exception:
                pass



        # ─── ascend Add-on Data (fail-safe) ───────────────────────────────────────
        mn_counterfactual_data = None
        mn_ontology_data = None
        mn_psych_data = None
        mn_incident_eligible = False
        mn_feedback_data = None

        if config.ASCEND_ENABLED and ASCEND_AVAILABLE:
            try:
                mn_counterfactual_data = mn_counterfactual.generate_counterfactuals(
                    report.risk_score, findings_serialized
                )
            except Exception:
                pass

            try:
                mn_ontology_data = mn_ontology.build_ontology(findings_serialized)
            except Exception:
                pass

            try:
                mn_psych_data = mn_psych.analyze_manipulation(
                    msg.get("subject", ""), msg.get("body_text", "")
                )
            except Exception:
                pass

            try:
                mn_incident_eligible = mn_incident.should_generate_report(report.risk_score)
            except Exception:
                pass

            try:
                mn_feedback_data = mn_rule_feedback.get_rule_feedback(message_id)
            except Exception:
                pass

        return render_template(
            "report.html",
            email=msg,
            report=report,
            findings_serialized=findings_serialized,
            analyzer_max=analyzer_max,
            trust_data=trust_data,
            existing_feedback=existing_feedback,
            feedback_available=FEEDBACK_AVAILABLE,
            killchain_data=killchain_data,
            linguistic_data=linguistic_data,
            campaign_data=campaign_data,
            header_graph_data=header_graph_data,

            domain_data=domain_data,
            safe_data=safe_data,
            psi_data=psi_data,
            confidence_data=confidence_data,
            # ── ascend data ──
            mn_counterfactual=mn_counterfactual_data,
            mn_ontology=mn_ontology_data,
            mn_psych=mn_psych_data,
            mn_incident_eligible=mn_incident_eligible,
            mn_feedback=mn_feedback_data,
        )

    except Exception as e:
        flash(f"Analysis failed: {str(e)}", "error")
        return redirect(url_for("inbox"))


@app.route("/history")
def history():
    """Show past analysis history."""
    logs = database.get_history()
    return render_template("history.html", logs=logs)


@app.route("/history/clear", methods=["POST"])
def clear_history():
    """Clear all analysis history and feedback."""
    try:
        conn = database.get_connection()
        conn.execute("DELETE FROM analysis_logs")
        conn.commit()
        # Also clear feedback if available
        if FEEDBACK_AVAILABLE:
            try:
                conn.execute("DELETE FROM user_feedback")
                conn.commit()
            except Exception:
                pass
        conn.close()
        return jsonify({"success": True, "message": "History cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Feature 3: User Feedback Routes ─────────────────────────────────────────


@app.route("/feedback/<message_id>", methods=["POST"])
def submit_feedback(message_id):
    """Accept user feedback for a specific email analysis."""
    if not FEEDBACK_AVAILABLE:
        return jsonify({"error": "Feedback module not available"}), 503

    try:
        data = request.get_json()
        feedback_value = data.get("feedback")
        original_score = data.get("original_score")
        original_level = data.get("original_level")

        if feedback_value not in ("phishing", "safe"):
            return jsonify({"error": "Invalid feedback value"}), 400

        feedback_module.submit_feedback(
            message_id=message_id,
            feedback=feedback_value,
            original_score=original_score,
            original_level=original_level,
        )
        return jsonify({"success": True, "message": f"Marked as {feedback_value}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/feedback/status/<message_id>")
def feedback_status(message_id):
    """Check if feedback exists for a message."""
    if not FEEDBACK_AVAILABLE:
        return jsonify({"feedback": None})

    try:
        fb = feedback_module.get_feedback(message_id)
        return jsonify({"feedback": fb})
    except Exception:
        return jsonify({"feedback": None})


# ─── Feature 4: Adaptive Weight Suggestions ──────────────────────────────────

@app.route("/admin/weights")
def admin_weights():
    """Display adaptive weight suggestions dashboard."""
    suggestions = {}
    feedback_stats = {}

    if WEIGHT_ADVISOR_AVAILABLE:
        try:
            suggestions = weight_advisor.compute_weight_suggestions()
        except Exception:
            suggestions = {"error": "Failed to compute suggestions"}

    if FEEDBACK_AVAILABLE:
        try:
            feedback_stats = feedback_module.get_feedback_stats()
        except Exception:
            pass

    return render_template(
        "admin.html",
        suggestions=suggestions,
        feedback_stats=feedback_stats,
        current_weights=config.SCORE_WEIGHTS,
    )


# ─── Feature 5: Weekly Security Summary Dashboard ────────────────────────────

@app.route("/dashboard")
def dashboard():
    """Display weekly security summary dashboard."""
    summary = {}

    if WEEKLY_SUMMARY_AVAILABLE:
        try:
            summary = weekly_summary.get_weekly_summary(days=7)
        except Exception:
            summary = {"error": "Failed to load summary"}

    profile_stats = {}
    weekly_trend = []
    if USER_PROFILE_AVAILABLE:
        try:
            profile_stats = user_profile.get_profile_stats()
            weekly_trend = user_profile.get_weekly_trend()
        except Exception:
            pass

    return render_template("dashboard.html", summary=summary, profile_stats=profile_stats, weekly_trend=weekly_trend)


# ─── v2 Feature 3: Campaign Detection Dashboard ──────────────────────────────

@app.route("/campaigns")
def campaigns():
    """Display detected phishing campaign clusters."""
    campaign_list = []
    if CAMPAIGN_AVAILABLE:
        try:
            campaign_list = campaign_detector.get_campaigns(limit=20)
        except Exception:
            pass
    return render_template("campaigns.html", campaigns=campaign_list)


# ─── v2 Feature 6: User Risk Profile ─────────────────────────────────────────

@app.route("/risk-profile")
def user_risk_profile():
    """Display user risk exposure profile."""
    profile = {}
    if RISK_PROFILE_AVAILABLE:
        try:
            profile = risk_profile_module.get_risk_profile(days=30)
        except Exception:
            profile = {"error": "Failed to compute risk profile"}
    return render_template("risk_profile.html", profile=profile)


# ─── v2 Feature 8: Forensic Evidence Export ──────────────────────────────────

@app.route("/export/<message_id>")
def export_forensic(message_id):
    """Generate and download a forensic evidence report as JSON."""
    if not FORENSIC_AVAILABLE:
        flash("Forensic export module not available.", "warning")
        return redirect(url_for("history"))

    try:
        # Retrieve the analysis log for this message
        conn = database.get_connection()
        row = conn.execute(
            "SELECT * FROM analysis_logs WHERE message_id = ? ORDER BY id DESC LIMIT 1",
            (message_id,),
        ).fetchone()
        conn.close()

        if not row:
            flash("No analysis found for this email.", "warning")
            return redirect(url_for("history"))

        log = dict(row)
        findings_list = json.loads(log.get("findings", "[]"))

        # Build a minimal RiskReport-like object for forensic export
        class _MinimalReport:
            def __init__(self, log_data):
                self.risk_score = log_data.get("risk_score", 0)
                self.risk_level = log_data.get("risk_level", "Unknown")
                self.intent = log_data.get("intent", "Unknown")
                self.explanation_summary = log_data.get("summary", "")
                self.analyzer_scores = {}
                self.awareness_tips = []
                self.findings = []

        minimal_report = _MinimalReport(log)
        email_meta = {
            "id": message_id,
            "subject": log.get("subject", ""),
            "sender": log.get("sender", ""),
            "date": log.get("timestamp", ""),
        }

        forensic_data = forensic_export.generate_forensic_report(
            email_meta, minimal_report, findings_list
        )
        json_str = forensic_export.format_report_json(forensic_data)

        from flask import Response
        return Response(
            json_str,
            mimetype="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=forensic_{message_id[:8]}.json"
            },
        )

    except Exception as e:
        flash(f"Export failed: {str(e)}", "error")
        return redirect(url_for("history"))


# ─── v2 Feature 10: Security Training Simulation ─────────────────────────────

@app.route("/training")
def training():
    """Display security training simulation landing page."""
    scenarios = []
    stats = {}
    if TRAINING_AVAILABLE:
        try:
            scenarios = training_sim.get_training_scenarios()
            stats = training_sim.get_training_stats()
        except Exception:
            pass
    return render_template("training.html", scenarios=scenarios, stats=stats)


@app.route("/training/<scenario_id>", methods=["GET", "POST"])
def training_scenario(scenario_id):
    """View a training scenario or evaluate a guess."""
    if not TRAINING_AVAILABLE:
        flash("Training module not available.", "warning")
        return redirect(url_for("training"))

    if request.method == "POST":
        user_guess = request.form.get("guess", "")
        result = training_sim.evaluate_user_guess(scenario_id, user_guess)
        scenario = training_sim.get_scenario_detail(scenario_id)
        return render_template("training.html",
                               scenario=scenario, result=result,
                               scenarios=training_sim.get_training_scenarios(),
                               stats=training_sim.get_training_stats())

    scenario = training_sim.get_scenario_detail(scenario_id)
    if not scenario:
        flash("Scenario not found.", "warning")
        return redirect(url_for("training"))
    return render_template("training.html",
                           scenario=scenario,
                           scenarios=training_sim.get_training_scenarios(),
                           stats=training_sim.get_training_stats())


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    database.init_db()
    app.run(debug=config.DEBUG, port=config.PORT)
