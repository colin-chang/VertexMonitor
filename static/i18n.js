// Vertex Monitor i18n — English (default) + 简体中文
(function() {
  var LANG_KEY = 'vm_lang';
  var messages = {
    en: {
      // Nav
      nav_title: 'Vertex Monitor',
      nav_dashboard: 'Dashboard',
      nav_settings: 'Settings',

      // Dashboard — Overview
      overview_title: 'Current Period',
      label_remaining: 'Remaining',
      label_spent: 'Spent',
      label_balance: 'Budget',
      label_expires: 'Expires',
      label_calls: 'calls',
      label_times: 'times',

      // Dashboard — Charts
      chart_cost_title: 'Cost Share',
      chart_token_title: 'Token Usage',
      chart_prompt: 'Prompt',
      chart_completion: 'Completion',
      chart_no_data: 'No data',

      // Dashboard — Table
      table_model: 'Model',
      table_calls: 'Calls',
      table_prompt: 'Prompt',
      table_completion: 'Completion',
      table_cost: 'Cost ($)',
      table_loading: 'Loading...',

      // Dashboard — History
      history_title: 'Recent Calls',
      history_time: 'Time',
      history_no_records: 'No call records',

      // Dashboard — Lifetime
      lifetime_title: 'Lifetime',
      lifetime_total_spent: 'Total Spent',
      lifetime_total_calls: 'Total Calls',

      // Dashboard — Status
      status_healthy: 'Healthy',
      status_warning: 'Warning',
      status_exhausted: 'Exhausted',

      // Settings — Key
      key_title: 'Vertex AI Credentials',
      key_status_ok: 'Configured',
      key_status_none: 'Not configured',
      key_label: 'Service Account JSON Key',
      key_placeholder: 'Paste the content of your vertex-key.json file...',
      key_hint: 'Paste the full content of your',
      key_hint_file: 'file into the textarea above',

      // Settings — Key Help
      key_help_title: 'How to obtain a Vertex AI Service Account Key',
      key_help_step1: 'Open',
      key_help_step2: 'Select your project (e.g. ai-project-384207)',
      key_help_step3: 'Click Create Credentials → Service Account',
      key_help_step4: 'Name your service account (e.g. vertex-monitor), click Create',
      key_help_step5: 'Assign role: Vertex AI User (or Vertex AI Administrator)',
      key_help_step6: 'After creation, click the account → Keys tab',
      key_help_step7: 'Click Add Key → Create New Key, choose JSON format',
      key_help_step8: 'Download the file, open it in a text editor, copy all content and paste above',
      key_help_security: 'Security notice: The key is stored only inside the local Docker container and is never uploaded to external services.',

      // Settings — Models
      models_title: 'Allowed Models',
      models_label: 'One model per line',
      models_hint: 'Only models in this list can be called through the proxy. Supports all vertex_ai/ model identifiers.',

      // Settings — Billing
      billing_title: 'Billing Mode',
      billing_auto: 'Auto Recurring',
      billing_manual: 'Manual',
      billing_reset_day: 'Monthly Reset Day',
      billing_monthly_amount: 'Monthly Amount ($)',
      billing_balance: 'Balance ($)',
      billing_expiry: 'Expiry Date',

      // Settings — Buttons
      btn_save: 'Save Settings',
      btn_saving: 'Saving...',
      btn_test: 'Test Connectivity',
      btn_testing: 'Testing...',
      btn_reset: 'Reset Current Period',
      hint_unsaved: 'Unsaved changes',

      // Settings — Test results
      test_ok: 'Connected',
      test_fail_save: 'Save failed',
      test_fail_conn: 'Connection failed',
      test_fail_net: 'Network error',

      // Settings — Validation
      val_model_empty: 'Model list cannot be empty',
      val_key_invalid_json: 'Key JSON is invalid',
      val_key_missing_fields: 'Key JSON missing required fields (private_key / client_email)',
      val_reset_day_range: 'Reset day must be between 1-28',
      val_amount_nonnegative: 'Amount must be >= 0',
      val_expiry_required: 'Expiry date is required',
      val_fix_errors: 'Please fix the following issues',
      val_save_failed: 'Settings save failed',
      val_billing_failed: 'Billing config save failed',
      val_network_error: 'Network error — check if proxy is running',

      // Settings — Notifications
      notify_saved: 'All settings saved',
      notify_reset: 'Period consumption reset',

      // Common
      common_or: 'or',
      common_confirm_reset: 'Reset current period consumption? Call records are kept, but spent resets to zero.',
    },
    'zh-CN': {
      nav_title: 'Vertex Monitor',
      nav_dashboard: '仪表盘',
      nav_settings: '设置',

      overview_title: '本期概览',
      label_remaining: '剩余额度',
      label_spent: '已消费',
      label_balance: '总预算',
      label_expires: '截止时间',
      label_calls: '调用',
      label_times: '次',

      chart_cost_title: '消费占比',
      chart_token_title: 'Token 用量',
      chart_prompt: 'Prompt',
      chart_completion: 'Completion',
      chart_no_data: '暂无数据',

      table_model: '模型',
      table_calls: '调用',
      table_prompt: 'Prompt',
      table_completion: 'Completion',
      table_cost: '消费 ($)',
      table_loading: '加载中...',

      history_title: '最近调用',
      history_time: '时间',
      history_no_records: '暂无调用记录',

      lifetime_title: '累计统计',
      lifetime_total_spent: '总消费',
      lifetime_total_calls: '总调用',

      status_healthy: '正常',
      status_warning: '即将耗尽',
      status_exhausted: '已耗尽',

      key_title: 'Vertex AI 凭证',
      key_status_ok: '已配置',
      key_status_none: '未配置',
      key_label: '服务账号 JSON Key',
      key_placeholder: '粘贴 vertex-key.json 文件内容...',
      key_hint: '将',
      key_hint_file: '文件内容完整粘贴到上方文本框',

      key_help_title: '如何获取 Vertex AI 服务账号 Key',
      key_help_step1: '打开',
      key_help_step2: '选择项目（如 ai-project-384207）',
      key_help_step3: '点击 创建凭据 → 服务账号',
      key_help_step4: '填写服务账号名称（如 vertex-monitor），点击创建',
      key_help_step5: '角色选择：Vertex AI User（或 Vertex AI Administrator）',
      key_help_step6: '创建完成后，点击该服务账号 → 密钥 标签页',
      key_help_step7: '点击 添加密钥 → 创建新密钥，选择 JSON 格式',
      key_help_step8: '下载文件，用文本编辑器打开，复制全部内容粘贴到上方文本框',
      key_help_security: '安全提醒：Key 仅存储在本地容器内，不会上传到任何外部服务。',

      models_title: '允许的模型列表',
      models_label: '每行一个模型名',
      models_hint: '仅列表中的模型可通过代理调用。支持所有 vertex_ai/ 模型标识。',

      billing_title: '计费模式设置',
      billing_auto: '自动循环',
      billing_manual: '手动设定',
      billing_reset_day: '每月重置日',
      billing_monthly_amount: '每月金额 ($)',
      billing_balance: '余额 ($)',
      billing_expiry: '截止日期',

      btn_save: '保存设置',
      btn_saving: '保存中...',
      btn_test: '测试连通性',
      btn_testing: '测试中...',
      btn_reset: '立即重置本期消费',
      hint_unsaved: '有未保存的修改',

      test_ok: '连通正常',
      test_fail_save: '保存失败',
      test_fail_conn: '连接失败',
      test_fail_net: '网络错误',

      val_model_empty: '模型列表不能为空',
      val_key_invalid_json: 'Key JSON 格式无效',
      val_key_missing_fields: 'Key JSON 缺少必要字段（private_key / client_email）',
      val_reset_day_range: '每月重置日必须在 1-28 之间',
      val_amount_nonnegative: '金额必须 >= 0',
      val_expiry_required: '截止日期不能为空',
      val_fix_errors: '请修正以下问题',
      val_save_failed: '设置保存失败',
      val_billing_failed: '计费配置保存失败',
      val_network_error: '网络错误，请检查代理服务是否运行',

      notify_saved: '所有设置已保存',
      notify_reset: '本期消费已重置',

      common_or: '或',
      common_confirm_reset: '确认立即重置本期消费？已有的消费记录不会被删除，但本期 spent 归零。',
    }
  };

  // ── Core ──
  function getLang() {
    return localStorage.getItem(LANG_KEY) || 'en';
  }

  function t(key) {
    var lang = getLang();
    return (messages[lang] && messages[lang][key]) || messages.en[key] || key;
  }

  function applyEl(el) {
    var key = el.getAttribute('data-i18n');
    if (!key) return;
    var text = t(key);
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      if (el.type === 'submit' || el.type === 'button') {
        el.value = text;
      } else {
        el.setAttribute('placeholder', text);
      }
    } else if (el.tagName === 'TITLE') {
      document.title = text;
    } else {
      el.textContent = text;
    }
  }

  // ── Apply all existing data-i18n elements ──
  function applyAll() {
    var els = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++) applyEl(els[i]);
  }

  // ── Public API ──
  window.i18n = {
    getLang: getLang,
    setLang: function(lang) {
      localStorage.setItem(LANG_KEY, lang);
      location.reload();
    },
    t: t,
    applyEl: applyEl,
    applyAll: applyAll,
    langs: ['en', 'zh-CN'],
    langLabels: { en: 'English', 'zh-CN': '简体中文' },
  };
})();
