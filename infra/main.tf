resource "fastly_service_vcl" "ceps" {
  name     = "ceps.cfms.dev"
  activate = true
  domain { name = "ceps.cfms.dev" }

  backend {
    name          = "GitHub Pages"
    address       = "cfms-dev.github.io"
    port          = 443
    override_host = "ceps.cfms.dev"

    use_ssl           = true
    ssl_check_cert    = true
    ssl_cert_hostname = "cfms-dev.github.io"
    ssl_sni_hostname  = "cfms-dev.github.io"
  }

  header {
    name          = "HSTS"
    type          = "response"
    action        = "set"
    destination   = "http.Strict-Transport-Security"
    ignore_if_set = false
    source        = "\"max-age=31536000; includeSubDomains; preload\""
  }

  request_setting {
    name      = "Force TLS"
    force_ssl = true
  }

  snippet {
    name    = "serve-rss"
    type    = "recv"
    content = <<-EOT
        if (req.url == "/ceps.rss/") {
          set req.url = "/ceps.rss";
        }
    EOT
  }

  snippet {
    name    = "topics"
    type    = "recv"
    content = <<-EOT
        if (req.url ~ "^/topics($|/)") {
          set req.http.Location = regsub(req.http.Location, "^/topics/?", "/topic/");
          error 618;
        }
    EOT
  }

  snippet {
    name    = "redirect"
    type    = "error"
    content = <<-EOT
        if (obj.status == 618) {
          set obj.status = 302;
          set obj.http.Location = "https://" + req.http.host + req.http.Location;
          return(deliver);
        }
    EOT
  }
  snippet {
    name    = "redirect-numbers"
    type    = "recv"
    content = <<-EOT
        if (req.url ~ "^/(\d|\d\d|\d\d\d|\d\d\d\d)/?$") {
          set req.http.Location = "/cep-" + std.strpad(re.group.1, 4, "0") + "/";
          error 618;
        }
    EOT
  }
  snippet {
    name    = "left-pad-cep-numbers"
    type    = "recv"
    content = <<-EOT
        if (req.url ~ "^/cep-(\d|\d\d|\d\d\d)/?$") {
          set req.http.Location = "/cep-" + std.strpad(re.group.1, 4, "0") + "/";
          error 618;
        }
    EOT
  }
}
