#!/bin/bash
#===============================================================================
# NEXUS-7 // Enterprise AI Demo Management Script
# Beyond the Prompt | Tim Spann | NYC AI Meetup 2026
#===============================================================================

set -e

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_FILE="app.py"
PORT="${NEXUS_PORT:-8509}"
CONNECTION="${SNOWFLAKE_CONNECTION_NAME:-tspann1}"
PID_FILE="$PROJECT_DIR/.nexus7.pid"
LOG_FILE="$PROJECT_DIR/.nexus7.log"

# Colors for Blade Runner theme
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
ORANGE='\033[0;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗    ███████╗     ║"
    echo "║  ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝    ╚════██║     ║"
    echo "║  ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗        ██╔╝     ║"
    echo "║  ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║       ██╔╝      ║"
    echo "║  ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║       ██║       ║"
    echo "║  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝       ╚═╝       ║"
    echo "║                                                               ║"
    echo "║  ENTERPRISE AI SYSTEM // \"MORE HUMAN THAN HUMAN\"             ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${CYAN}[NEXUS-7]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[NEXUS-7]${NC} $1"
}

log_error() {
    echo -e "${RED}[NEXUS-7]${NC} $1"
}

log_warn() {
    echo -e "${ORANGE}[NEXUS-7]${NC} $1"
}

check_uv() {
    if ! command -v uv &> /dev/null; then
        log_error "UV not found. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
}

setup() {
    banner
    log_info "Setting up NEXUS-7 environment..."
    
    check_uv
    
    cd "$PROJECT_DIR"
    
    # Create virtual environment and install deps
    log_info "Creating virtual environment with UV..."
    uv venv
    
    log_info "Installing dependencies..."
    uv pip install -e .
    
    log_success "Environment setup complete!"
    log_info "Activate with: source .venv/bin/activate"
}

start() {
    banner
    log_info "Initializing NEXUS-7 systems..."
    
    cd "$PROJECT_DIR"
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warn "NEXUS-7 already running (PID: $PID)"
            log_info "Access: http://localhost:$PORT"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    # Kill any existing process on the port
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
    
    # Activate venv if exists, otherwise use system
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    log_info "Starting Streamlit on port $PORT..."
    log_info "Connection: $CONNECTION"
    
    # Start in background
    SNOWFLAKE_CONNECTION_NAME="$CONNECTION" \
    nohup streamlit run "$APP_FILE" \
        --server.port "$PORT" \
        --server.headless true \
        --server.address 0.0.0.0 \
        > "$LOG_FILE" 2>&1 &
    
    echo $! > "$PID_FILE"
    
    # Wait for startup
    sleep 3
    
    if [ -f "$PID_FILE" ] && ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        log_success "NEXUS-7 ONLINE"
        echo -e "${MAGENTA}"
        echo "┌─────────────────────────────────────────────────────────────┐"
        echo "│ LOCAL URL:    http://localhost:$PORT                        │"
        echo "│ CONNECTION:   $CONNECTION                                  │"
        echo "│ PID:          $(cat $PID_FILE)                                              │"
        echo "│ LOG:          $LOG_FILE         │"
        echo "└─────────────────────────────────────────────────────────────┘"
        echo -e "${NC}"
    else
        log_error "Failed to start NEXUS-7. Check logs:"
        tail -20 "$LOG_FILE"
        return 1
    fi
}

stop() {
    banner
    log_info "Shutting down NEXUS-7..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID" 2>/dev/null || true
            sleep 2
            # Force kill if still running
            kill -9 "$PID" 2>/dev/null || true
            log_success "NEXUS-7 terminated (PID: $PID)"
        else
            log_warn "Process not found (stale PID file)"
        fi
        rm -f "$PID_FILE"
    else
        log_warn "No PID file found"
    fi
    
    # Also kill by port
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    log_success "NEXUS-7 OFFLINE"
}

restart() {
    stop
    sleep 2
    start
}

status() {
    banner
    log_info "NEXUS-7 System Status"
    echo ""
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_success "STATUS: ONLINE"
            echo -e "${CYAN}┌─────────────────────────────────────────────────────────────┐${NC}"
            echo -e "${CYAN}│${NC} PID:          $PID"
            echo -e "${CYAN}│${NC} PORT:         $PORT"
            echo -e "${CYAN}│${NC} URL:          http://localhost:$PORT"
            echo -e "${CYAN}│${NC} CONNECTION:   $CONNECTION"
            echo -e "${CYAN}│${NC} UPTIME:       $(ps -o etime= -p $PID | xargs)"
            echo -e "${CYAN}│${NC} MEMORY:       $(ps -o rss= -p $PID | awk '{printf "%.1f MB", $1/1024}')"
            echo -e "${CYAN}└─────────────────────────────────────────────────────────────┘${NC}"
        else
            log_error "STATUS: OFFLINE (stale PID)"
            rm -f "$PID_FILE"
        fi
    else
        log_error "STATUS: OFFLINE"
    fi
}

logs() {
    banner
    log_info "NEXUS-7 System Logs"
    echo ""
    
    if [ -f "$LOG_FILE" ]; then
        if [ "$1" == "-f" ] || [ "$1" == "--follow" ]; then
            tail -f "$LOG_FILE"
        else
            tail -50 "$LOG_FILE"
        fi
    else
        log_warn "No log file found"
    fi
}

validate() {
    banner
    log_info "Running NEXUS-7 full validation suite..."
    echo ""
    
    cd "$PROJECT_DIR"
    
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    python3 validate.py
    local rc=$?
    
    echo ""
    if [ $rc -eq 0 ]; then
        log_success "Validation complete!"
    else
        log_error "Validation found issues — review output above"
    fi
    return $rc
}

run_tests() {
    banner
    log_info "Running pytest suite..."
    echo ""
    
    cd "$PROJECT_DIR"
    
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    uv run pytest tests/ -v --tb=short
    local rc=$?
    
    echo ""
    if [ $rc -eq 0 ]; then
        log_success "All tests passed!"
    else
        log_error "Some tests failed — review output above"
    fi
    return $rc
}

build_pptx() {
    banner
    log_info "Generating PowerPoint slides..."
    echo ""
    
    cd "$PROJECT_DIR"
    
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    uv run python3 build_pptx.py
    local rc=$?
    
    if [ $rc -eq 0 ]; then
        log_success "PowerPoint generated: presentation.pptx"
    else
        log_error "PowerPoint generation failed"
    fi
    return $rc
}

usage() {
    banner
    echo -e "${MAGENTA}NEXUS-7 Management Commands:${NC}"
    echo ""
    echo "  ./manage.sh setup      - Initialize UV environment and dependencies"
    echo "  ./manage.sh start      - Start the Streamlit application"
    echo "  ./manage.sh stop       - Stop the application"
    echo "  ./manage.sh restart    - Restart the application"
    echo "  ./manage.sh status     - Show application status"
    echo "  ./manage.sh logs       - Show recent logs"
    echo "  ./manage.sh logs -f    - Follow logs in real-time"
    echo "  ./manage.sh validate   - Run full validation suite"
    echo "  ./manage.sh test       - Run pytest test suite"
    echo "  ./manage.sh pptx       - Generate PowerPoint slides"
    echo ""
    echo -e "${CYAN}Environment Variables:${NC}"
    echo "  NEXUS_PORT                 - Port number (default: 8509)"
    echo "  SNOWFLAKE_CONNECTION_NAME  - Snowflake connection (default: tspann1)"
    echo ""
}

# Main
case "${1:-}" in
    setup)
        setup
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "${2:-}"
        ;;
    validate)
        validate
        ;;
    test)
        run_tests
        ;;
    pptx)
        build_pptx
        ;;
    *)
        usage
        ;;
esac
