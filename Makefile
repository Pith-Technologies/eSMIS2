# eSMIS security scanning targets.
#
# These are the scanners that do not belong in `./esmis`: they run against a
# built image or a live server rather than the source tree, and CI invokes
# them through .github/workflows/security.yml rather than through here.
# Everything else — building, running, testing, linting, auditing — is
# `./esmis`, which is the single entry point.

.PHONY: help zap-scan trivy-scan gitleaks-scan dependency-scan

# Default target
help:
	@echo "eSMIS security scanning (local use)"
	@echo ""
	@echo "  make zap-scan             Run OWASP ZAP baseline scan (requires running Odoo)"
	@echo "  make trivy-scan           Run Trivy container image scan"
	@echo "  make gitleaks-scan        Run Gitleaks secret detection"
	@echo "  make dependency-scan      Run dependency vulnerability scan"

# ============================================
# Security Scanning - Individual Tools
# ============================================

zap-scan:
	@echo "Running OWASP ZAP baseline scan..."
	@chmod +x scripts/zap/run-baseline.sh
	./scripts/zap/run-baseline.sh

trivy-scan:
	@echo "Running Trivy container image scan..."
	@chmod +x scripts/trivy/run-trivy.sh
	./scripts/trivy/run-trivy.sh

gitleaks-scan:
	@echo "Running Gitleaks secret detection..."
	@chmod +x scripts/gitleaks/run-gitleaks.sh
	./scripts/gitleaks/run-gitleaks.sh

dependency-scan:
	@echo "Running dependency vulnerability scan..."
	@chmod +x scripts/dependency-scan.sh
	./scripts/dependency-scan.sh
