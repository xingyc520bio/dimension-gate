/**
 * 维度之门 - 提交留资表单 API
 * Cloudflare Pages Function + D1
 * POST /api/submit
 */

export async function onRequestPost(context) {
  const { request, env } = context;
  const db = env.DB;

  // CORS headers
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  try {
    const data = await request.json();

    const name = (data.name || '').trim();
    const company = (data.company || '').trim();
    const phone = (data.phone || '').trim();
    const interests = Array.isArray(data.interests) ? data.interests.join(',') : String(data.interests || '');
    const message = (data.message || '').trim();

    // Validation
    if (!name) return Response.json({ ok: false, error: '姓名不能为空' }, { status: 400, headers });
    if (!company) return Response.json({ ok: false, error: '公司名称不能为空' }, { status: 400, headers });
    if (!phone) return Response.json({ ok: false, error: '联系电话不能为空' }, { status: 400, headers });

    const phoneClean = phone.replace(/[\s\-]/g, '');
    const phoneRe = /^(\+?86)?1[3-9]\d{9}$|^\+?[0-9]{8,15}$/;
    if (!phoneRe.test(phoneClean)) {
      return Response.json({ ok: false, error: '请输入有效的手机号码' }, { status: 400, headers });
    }
    if (message.length > 200) {
      return Response.json({ ok: false, error: '留言不能超过200字' }, { status: 400, headers });
    }

    const createdAt = new Date().toISOString().replace('T', ' ').slice(0, 19);

    const result = await db.prepare(
      'INSERT INTO submissions (name, company, phone, interests, message, created_at) VALUES (?, ?, ?, ?, ?, ?)'
    ).bind(name, company, phone, interests, message, createdAt).run();

    return Response.json(
      { ok: true, id: result.meta.last_row_id, message: '提交成功，我们将在24小时内联系您！' },
      { status: 200, headers }
    );
  } catch (err) {
    return Response.json(
      { ok: false, error: '服务器错误，请稍后重试' },
      { status: 500, headers }
    );
  }
}

// Handle CORS preflight
export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
