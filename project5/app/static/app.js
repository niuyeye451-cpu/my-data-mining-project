/**
 * 工业商城搜索引擎 — 前端交互 JS
 */

document.addEventListener('DOMContentLoaded', () => {

    // ── 注册页：密码一致性校验 ──
    const regForm = document.getElementById('register-form');
    if (regForm) {
        const pw = document.getElementById('password');
        const pw2 = document.getElementById('confirm_password');
        const err = document.getElementById('password-error');

        function validate() {
            if (pw2.value && pw.value !== pw2.value) {
                pw2.classList.add('border-error');
                if (err) err.classList.remove('hidden');
                return false;
            } else {
                pw2.classList.remove('border-error');
                if (err) err.classList.add('hidden');
                return true;
            }
        }

        pw.addEventListener('input', validate);
        pw2.addEventListener('input', validate);

        regForm.addEventListener('submit', (e) => {
            if (!validate()) e.preventDefault();
        });
    }
});

// ── 搜索页：VIP 切换跳转 ──
function toggleVIP(cb) {
    const params = new URLSearchParams(window.location.search);
    if (cb.checked) {
        params.set('vip', '1');
    } else {
        params.delete('vip');
    }
    params.set('page', '1');
    window.location.search = params.toString();
}

// ── 搜索页：排序切换 ──
function changeSort(val) {
    const params = new URLSearchParams(window.location.search);
    params.set('sort', val);
    params.set('page', '1');
    window.location.search = params.toString();
}

// ── 搜索页：价格区间验证 ──
document.addEventListener('submit', (e) => {
    const form = e.target.closest('form[action="/"]');
    if (!form) return;
    const minEl = form.querySelector('input[name="price_min"]');
    const maxEl = form.querySelector('input[name="price_max"]');
    if (!minEl || !maxEl) return;
    const min = minEl.value.trim();
    const max = maxEl.value.trim();
    if (!min && !max) return; // 两个都空，正常提交
    if ((min && !max) || (!min && max)) {
        e.preventDefault();
        alert('请输入完整的价格区间（最低和最高都需要填写）');
        return;
    }
    if (parseFloat(min) < 0 || parseFloat(max) < 0) {
        e.preventDefault();
        alert('价格不能为负数');
        return;
    }
    if (parseFloat(min) >= parseFloat(max)) {
        e.preventDefault();
        alert('最低价格必须小于最高价格');
        return;
    }
});
