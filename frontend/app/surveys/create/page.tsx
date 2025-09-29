'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function CreateSurveyPage() {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [saving, setSaving] = useState(false);
  const [ok, setOk] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSaving(true); setOk(null); setErr(null);

    try {
      const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${base}/surveys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description: desc }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setOk(`已建立 #${data.id}`);
      setTitle('');
      setDesc('');
    } catch (e: any) {
      setErr(e?.message ?? '發生錯誤');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-10">
      <h1 className="text-2xl font-bold mb-6">建立問卷</h1>

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">標題</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded border px-3 py-2"
            placeholder="我的問卷"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">描述</label>
          <textarea
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            className="w-full rounded border px-3 py-2"
            rows={4}
            placeholder="想問的重點、背景說明…"
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            disabled={saving}
            className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
          >
            {saving ? '建立中…' : '建立'}
          </button>
          <Link href="/surveys" className="text-gray-600 hover:underline">
            回列表
          </Link>
        </div>

        {ok && <p className="text-green-600">{ok}</p>}
        {err && <p className="text-red-600">{err}</p>}
      </form>
    </div>
  );
}
