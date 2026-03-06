/**
 * 维度之门 - 查看提交记录 API（管理用）
 * Cloudflare Pages Function + D1
 * GET /api/submissions?token=xxx
 */

export async function onRequestGet(context) {
  const { request, env } = context;
  const db = env.DB;

  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
  };

  const url = new URL(request.url);
  const token = url.searchParams.get('token') || '';
  const adminToken = env.ADMIN_TOKEN || 'dimensiongate2025';

  if (token !== adminToken) {
    return Response.json({ ok: false, error: 'Unauthorized' }, { status: 401, headers });
  }

  try {
    const { results } = await db.prepare(
      'SELECT id, name, company, phone, interests, message, created_at FROM submissions ORDER BY id DESC'
    ).all();

    return Response.json(
      { ok: true, total: results.length, data: results },
      { status: 200, headers }
    );
  } catch (err) {
    return Response.json(
      { ok: false, error: '数据库查询失败' },
      { status: 500, headers }
    );
  }
}
