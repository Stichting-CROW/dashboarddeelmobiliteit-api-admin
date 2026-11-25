import html
import markdown

PROJECT_NAME = "Dashboard Deelmobiliteit"
CONTACT_EMAIL = "info@dashboarddeelmobiliteit.nl"
DASHBOARD_URL = "https://dashboarddeelmobiliteit.nl"

# Colors mirror the frontend logo (LogoDashboardDeelmobiliteit.tsx)
COLOR_TEXT = "#343E47"
COLOR_ACCENT = "#15AEEF"
COLOR_BACKGROUND = "#F3F4F6"
COLOR_MUTED = "#6B7280"

FONT_STACK = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def markdown_to_html(body_markdown: str) -> str:
    """Convert Markdown to an HTML fragment."""
    return markdown.markdown(
        body_markdown or "",
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5"
    )


def render_html(subject: str, body_markdown: str) -> str:
    """Wrap the converted Markdown in the branded e-mail template.

    Styles are inline (or in a <style> block with element selectors) because
    most e-mail clients strip external stylesheets and many ignore classes.
    """
    body_html = markdown_to_html(body_markdown)
    safe_subject = html.escape(subject or PROJECT_NAME)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_subject}</title>
  <style>
    body {{ margin: 0; padding: 0; background-color: {COLOR_BACKGROUND}; }}
    .content h1 {{ font-size: 22px; line-height: 28px; margin: 24px 0 12px; color: {COLOR_TEXT}; font-weight: 700; }}
    .content h2 {{ font-size: 18px; line-height: 24px; margin: 22px 0 10px; color: {COLOR_TEXT}; font-weight: 700; }}
    .content h3 {{ font-size: 16px; line-height: 22px; margin: 20px 0 8px; color: {COLOR_TEXT}; font-weight: 700; }}
    .content h1:first-child, .content h2:first-child, .content h3:first-child, .content p:first-child {{ margin-top: 0; }}
    .content p {{ font-size: 15px; line-height: 24px; margin: 0 0 16px; color: {COLOR_TEXT}; }}
    .content ul, .content ol {{ font-size: 15px; line-height: 24px; margin: 0 0 16px; padding-left: 24px; color: {COLOR_TEXT}; }}
    .content li {{ margin-bottom: 4px; }}
    .content a {{ color: {COLOR_ACCENT}; text-decoration: underline; }}
    .content strong {{ font-weight: 700; }}
    .content blockquote {{ margin: 0 0 16px; padding: 8px 16px; border-left: 3px solid {COLOR_ACCENT}; color: {COLOR_MUTED}; }}
    .content hr {{ border: 0; border-top: 1px solid #E5E7EB; margin: 24px 0; }}
    .content img {{ max-width: 100%; height: auto; }}
    .content table {{ border-collapse: collapse; margin: 0 0 16px; font-size: 14px; }}
    .content th, .content td {{ border: 1px solid #E5E7EB; padding: 6px 10px; text-align: left; }}
    .content code {{ font-family: Menlo, Consolas, monospace; font-size: 13px; background: #F3F4F6; padding: 1px 4px; border-radius: 3px; }}
    .content pre {{ background: #F3F4F6; padding: 12px; border-radius: 6px; overflow-x: auto; }}
  </style>
</head>
<body style="margin:0; padding:0; background-color:{COLOR_BACKGROUND};">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:{COLOR_BACKGROUND};">
    <tr>
      <td align="center" style="padding: 32px 16px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="width:100%; max-width:600px;">
          <tr>
            <td style="padding: 0 8px 20px 8px; font-family: {FONT_STACK};">
              <a href="{DASHBOARD_URL}" style="text-decoration:none; color:{COLOR_TEXT};">
                <div style="font: normal normal bold 20px/24px {FONT_STACK}; color: {COLOR_TEXT};">{PROJECT_NAME}</div>
              </a>
              <div style="width:155px; margin-top:4px; border-bottom:3px solid {COLOR_ACCENT};"></div>
            </td>
          </tr>
          <tr>
            <td style="background-color:#FFFFFF; border-radius:12px; padding: 32px; font-family: {FONT_STACK}; color: {COLOR_TEXT};">
              <div class="content">
{body_html}
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 8px 0 8px; font-family: {FONT_STACK}; font-size: 12px; line-height: 18px; color: {COLOR_MUTED};">
              Je ontvangt deze e-mail omdat je een account hebt bij het {PROJECT_NAME}. Vragen? Mail naar <a href="mailto:{CONTACT_EMAIL}" style="color:{COLOR_MUTED};">{CONTACT_EMAIL}</a>.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def render_text(subject: str, body_markdown: str) -> str:
    """Plain-text alternative: the Markdown source with a simple header/footer."""
    return (
        f"{PROJECT_NAME}\n"
        f"{'=' * len(PROJECT_NAME)}\n\n"
        f"{body_markdown or ''}\n\n"
        f"--\n"
        f"Je ontvangt deze e-mail omdat je een account hebt bij het {PROJECT_NAME}.\n"
        f"Vragen? Mail naar {CONTACT_EMAIL}.\n"
    )
