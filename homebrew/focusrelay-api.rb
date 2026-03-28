class FocusrelayApi < Formula
  include Language::Python::Virtualenv

  desc "HTTP API server for OmniFocus via FocusRelayMCP"
  homepage "https://github.com/jenrzzz/focusrelay-api"
  url "https://github.com/jenrzzz/focusrelay-api/archive/refs/tags/v0.2.1.tar.gz"
  sha256 "6bf6ca5b839704d55c0a983b8769d77a9c7536f5f7f94a66ce09110bccef023d"
  license "MIT"

  depends_on "deverman/focus-relay/focusrelay"
  depends_on "python@3.13"

  def install
    virtualenv_create(libexec, "python3.13")
    system libexec/"bin/pip", "install", *std_pip_args, "."
    (bin/"focusrelay-api").write_env_script(libexec/"bin/focusrelay-api", PATH: "#{libexec}/bin:$PATH")
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
    sleep 3
    output = shell_output("curl -s http://127.0.0.1:#{port}/health 2>&1", 0)
    assert_match(/error|ok/, output)
  ensure
    Process.kill("TERM", pid)
    Process.wait(pid)
  end
end
