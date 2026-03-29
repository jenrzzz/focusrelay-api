class FocusrelayApi < Formula
  desc "HTTP API server for OmniFocus via FocusRelayMCP"
  homepage "https://github.com/jenrzzz/focusrelay-api"
  url "https://github.com/jenrzzz/focusrelay-api/archive/refs/tags/v0.2.2.tar.gz"
  sha256 "1f37b9fb9608c970448c258dbdb603d1d462adcd78ace88e98b058f427d8377f"
  license "MIT"

  depends_on "deverman/focus-relay/focusrelay"
  depends_on "uv"

  def install
    # Install source preserving src layout, then pip install into a venv
    libexec.install Dir["src", "pyproject.toml"]
    python = Formula["python@3.13"].opt_bin/"python3.13"
    system "uv", "venv", "--python=#{python}", libexec/".venv"
    system "uv", "pip", "install", "--python=#{libexec}/.venv/bin/python3.13", libexec.to_s

    (bin/"focusrelay-api").write <<~BASH
      #!/bin/bash
      exec "#{libexec}/.venv/bin/focusrelay-api" "$@"
    BASH
  end

  def caveats
    <<~EOS
      Start the server:
        focusrelay-api

      Configure via environment variables:
        FOCUSRELAY_BIN        Path to focusrelay binary (default: focusrelay)
        FOCUSRELAY_API_TOKEN  Bearer token for auth (default: disabled)
        FOCUSRELAY_HOST       Bind address (default: 0.0.0.0)
        FOCUSRELAY_PORT       Port (default: 8394)

      To run as a background service:
        brew services start jenrzzz/formulae/focusrelay-api

      API docs: http://localhost:8394/docs
    EOS
  end

  service do
    run opt_bin/"focusrelay-api"
    keep_alive true
    log_path var/"log/focusrelay-api.log"
    error_log_path var/"log/focusrelay-api.log"
    working_dir HOMEBREW_PREFIX
  end

  test do
    port = free_port
    pid = fork do
      ENV["FOCUSRELAY_PORT"] = port.to_s
      ENV["FOCUSRELAY_HOST"] = "127.0.0.1"
      exec bin/"focusrelay-api"
    end
    sleep 5
    output = shell_output("curl -s http://127.0.0.1:#{port}/health 2>&1", 0)
    assert_match(/error|ok/, output)
  ensure
    Process.kill("TERM", pid)
    Process.wait(pid)
  end
end
