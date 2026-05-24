/* ── Shared Utilities ── */
function escHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

/* ── Notify Modal ── */
function notify(icon, msg) {
  document.getElementById('notifyIcon').textContent = icon;
  document.getElementById('notifyMsg').innerHTML = msg;
  document.getElementById('notifyModal').classList.add('show');
}
function closeNotify(e) {
  if (e && e.target !== document.getElementById('notifyModal')) return;
  document.getElementById('notifyModal').classList.remove('show');
}

/* ── Help Modal ── */
function openHelp(title, bodyHtml) {
  document.getElementById('helpTitle').textContent = title;
  document.getElementById('helpBody').innerHTML = bodyHtml;
  document.getElementById('helpModal').classList.add('show');
}
function closeHelp(e) {
  if (e && e.target !== document.getElementById('helpModal')) return;
  document.getElementById('helpModal').classList.remove('show');
}

/* ── Keyboard ── */
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { closeNotify(); closeHelp(); }
});

/* ── Agent Help ── */
function showAgentHelp() {
  openHelp(i18n.t('agent_help_title'),
    '<p>' + i18n.t('agent_help_desc') + '</p>' +
    '<p style="margin-top:8px;"><strong>' + i18n.t('agent_help_endpoint') + ':</strong> <code>POST /v1/chat/completions</code></p>' +
    '<p style="margin-top:14px;"><strong>' + i18n.t('agent_help_hermes') + '</strong></p>' +
    '<ol>' +
    '<li>' + i18n.t('agent_help_step1') + '</li>' +
    '<li>' + i18n.t('agent_help_step2') + '</li>' +
    '</ol>' +
    '<pre><code>' + escHtml(i18n.t('agent_help_config')) + '</code></pre>' +
    '<p style="margin-top:4px;">3. ' + i18n.t('agent_help_step3') + '</p>' +
    '<p style="margin-top:10px;">💡 <strong>' + i18n.t('agent_help_note_label') + '</strong> ' + i18n.t('agent_help_note') + '</p>' +
    '<hr style="border:none;border-top:1px solid var(--border);margin:16px 0;">' +
    '<p><strong>' + i18n.t('agent_help_skill_title') + '</strong></p>' +
    '<p style="margin-top:4px;">' + i18n.t('agent_help_skill_desc') + '</p>' +
    '<p style="margin-top:12px;"><strong>' + i18n.t('agent_help_skill_install') + '</strong></p>' +
    '<p style="margin-top:4px;">' + i18n.t('agent_help_skill_install_desc') + '</p>' +
    '<pre><code>' + escHtml(i18n.t('agent_help_skill_install_claude')) + ':  ~/.claude/skills/vertex-monitor/SKILL.md\n' +
      escHtml(i18n.t('agent_help_skill_install_hermes')) + ':    ~/.hermes/skills/vertex-monitor/SKILL.md\n' +
      escHtml(i18n.t('agent_help_skill_install_generic')) + ':  &lt;project&gt;/.agents/skills/vertex-monitor/SKILL.md</code></pre>' +
    '<p style="margin-top:12px;"><strong>' + i18n.t('agent_help_skill_usage') + '</strong></p>' +
    '<p style="margin-top:4px;">' + i18n.t('agent_help_skill_usage_desc') + '</p>' +
    '<ul style="margin-top:6px;padding-left:20px;font-size:13px;line-height:2;">' +
    '<li>' + i18n.t('agent_help_skill_usage_ex1') + '</li>' +
    '<li>' + i18n.t('agent_help_skill_usage_ex2') + '</li>' +
    '<li>' + i18n.t('agent_help_skill_usage_ex3') + '</li>' +
    '</ul>'
  );
}

/* ── Balance Help ── */
function showBalanceHelp() {
  openHelp(i18n.t('balance_help_title'),
    '<ol>' +
    '<li>' + i18n.t('balance_help_step1') + ' <a href="https://console.cloud.google.com/billing" target="_blank" rel="noopener">Google Cloud Console → Billing</a></li>' +
    '<li>' + i18n.t('balance_help_step2') + '</li>' +
    '<li>' + i18n.t('balance_help_step3') + '</li>' +
    '<li>' + i18n.t('balance_help_step4') + '</li>' +
    '</ol>' +
    '<p style="margin-top:10px;">💡 <strong>' + i18n.t('balance_help_tip_label') + '</strong> ' + i18n.t('balance_help_tip') + '</p>'
  );
}
