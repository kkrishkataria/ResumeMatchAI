import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function SkillList({ title, skills, tone = 'slate' }) {
  const colors = {
    slate: 'bg-slate-100 text-slate-700',
    green: 'bg-emerald-100 text-emerald-800',
    amber: 'bg-amber-100 text-amber-800',
  }
  return <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <h3 className="font-semibold text-slate-900">{title}</h3>
    {skills.length ? <div className="mt-3 flex flex-wrap gap-2">{skills.map(skill => <span key={skill} className={`rounded-full px-3 py-1 text-sm font-medium ${colors[tone]}`}>{skill}</span>)}</div> : <p className="mt-3 text-sm text-slate-500">No recognized skills found.</p>}
  </section>
}

function ScoreRing({ score }) {
  return <div
    className="grid h-36 w-36 shrink-0 place-items-center rounded-full"
    style={{ background: `conic-gradient(#5eead4 ${score * 3.6}deg, rgba(255, 255, 255, 0.18) 0deg)` }}
    role="img"
    aria-label={`Skill similarity: ${score}%`}
  >
    <div className="grid h-[112px] w-[112px] place-items-center rounded-full bg-ink"><strong className="text-3xl tracking-tight text-white">{score}%</strong></div>
  </div>
}

function HistoryCard({ item, onDelete, deleting }) {
  const analyzedAt = new Date(item.timestamp)
  const dateLabel = Number.isNaN(analyzedAt.getTime())
    ? 'Date unavailable'
    : analyzedAt.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
  const requiredSkills = item.matched_skills.length + item.missing_skills.length
  const skillCoverage = requiredSkills ? Math.round((item.matched_skills.length / requiredSkills) * 100) : null

  return <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <div className="flex items-start justify-between gap-4">
      <div><p className="text-xs font-semibold tracking-wide text-slate-500">{item.score_type === 'skill' ? 'SKILL SIMILARITY' : 'TEXT SIMILARITY (OLDER)'}</p><strong className="mt-1 block text-3xl tracking-tight text-ink">{item.score}%</strong>{skillCoverage !== null && <p className="mt-1 text-sm font-medium text-teal-700">{item.matched_skills.length} of {requiredSkills} recognized job skills matched</p>}</div>
      <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700">{dateLabel}</span>
    </div>
    {item.job_summary && <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">{item.job_summary}</p>}
    <div className="mt-4 grid gap-4 border-t border-slate-100 pt-4 sm:grid-cols-2">
      <div><p className="text-xs font-semibold tracking-wide text-emerald-700">MATCHED · {item.matched_skills.length}</p><div className="mt-2 flex flex-wrap gap-1.5">{item.matched_skills.length ? item.matched_skills.map(skill => <span key={skill} className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800">{skill}</span>) : <span className="text-sm text-slate-500">None</span>}</div></div>
      <div><p className="text-xs font-semibold tracking-wide text-amber-700">MISSING · {item.missing_skills.length}</p><div className="mt-2 flex flex-wrap gap-1.5">{item.missing_skills.length ? item.missing_skills.map(skill => <span key={skill} className="rounded-full bg-amber-100 px-2 py-1 text-xs font-medium text-amber-800">{skill}</span>) : <span className="text-sm text-slate-500">None found</span>}</div></div>
    </div>
    <button onClick={() => onDelete(item.id)} disabled={deleting} aria-label="Delete analysis" title="Delete analysis" className="mt-5 inline-flex h-9 w-9 items-center justify-center rounded-lg text-red-600 transition hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:opacity-50">
      {deleting ? <span className="text-xs">…</span> : <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5" aria-hidden="true"><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /><path d="M10 11v5M14 11v5" /></svg>}
    </button>
  </article>
}

function App() {
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  const loadHistory = async () => {
    try { const response = await fetch(`${API_URL}/history`); setHistory(await response.json()) } catch { setHistory({ available: false, message: 'Backend is not reachable yet.' }) }
  }
  useEffect(() => { loadHistory() }, [])

  const deleteHistoryItem = async (id) => {
    setDeletingId(id)
    try {
      const response = await fetch(`${API_URL}/history/${id}`, { method: 'DELETE' })
      const body = await response.json()
      if (!response.ok) throw new Error(body.detail || 'Could not delete this analysis.')
      await loadHistory()
    } catch (err) { setError(err.message || 'Could not delete this analysis.') } finally { setDeletingId(null) }
  }

  const analyze = async (event) => {
    event.preventDefault(); setError(''); setResult(null)
    if (!file) return setError('Choose a PDF resume to continue.')
    if (!jobDescription.trim()) return setError('Paste a job description to continue.')
    if (file.type && file.type !== 'application/pdf') return setError('Please choose a PDF file.')
    if (file.size > 5 * 1024 * 1024) return setError('Please choose a PDF smaller than 5 MB.')
    setLoading(true)
    const data = new FormData(); data.append('resume', file); data.append('job_description', jobDescription)
    try {
      const response = await fetch(`${API_URL}/analyze`, { method: 'POST', body: data })
      const body = await response.json()
      if (!response.ok) throw new Error(body.detail || 'Analysis failed. Please try again.')
      setResult(body); loadHistory()
    } catch (err) { setError(err.message || 'Could not connect to the backend.') } finally { setLoading(false) }
  }
  const editAnalysis = () => { setResult(null); setError('') }
  const reset = () => { setFile(null); setJobDescription(''); setResult(null); setError('') }

  return <main className="min-h-screen bg-paper">
    <header className="border-b border-slate-200 bg-white"><div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4"><span className="text-lg font-bold tracking-tight">ResumeMatch <span className="text-teal-600">AI</span></span><span className="hidden text-sm text-slate-500 sm:block">Explainable resume matching for students</span></div></header>
    <div className="mx-auto max-w-6xl px-5 py-12">
      <section className="grid gap-8 pb-12 md:grid-cols-[1.2fr_.8fr] md:items-center">
        <div><p className="mb-3 inline-block rounded-full bg-teal-100 px-3 py-1 text-xs font-semibold tracking-wide text-teal-800">TF-IDF + COSINE SIMILARITY</p><h1 className="text-4xl font-bold tracking-tight text-ink sm:text-5xl">See how your resume aligns with a role.</h1><p className="mt-5 max-w-xl text-lg leading-8 text-slate-600">Upload a text-based PDF and paste a job description. Get an explainable keyword match score and a focused view of recognized skill gaps.</p></div>
        <aside className="rounded-3xl bg-ink p-7 text-white shadow-xl"><p className="text-sm font-semibold text-mint">WHAT THE SCORE MEANS</p><p className="mt-3 text-xl font-semibold">A text-overlap signal, not a hiring prediction.</p><p className="mt-3 text-sm leading-6 text-slate-300">ResumeMatch compares terms using TF-IDF. It cannot evaluate experience quality, projects, or potential.</p></aside>
      </section>
      {!result ? <form onSubmit={analyze} className="grid gap-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
        <label className="block"><span className="text-sm font-semibold">1. Upload your resume</span><span className="mt-1 block text-sm text-slate-500">PDF only · maximum 5 MB · files are analyzed in memory</span><input id="resume-file" type="file" accept="application/pdf,.pdf" className="mt-4 block w-full rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-teal-600 file:px-3 file:py-2 file:font-medium file:text-white" onChange={e => setFile(e.target.files[0] || null)} />{file && <p className="mt-2 text-sm text-teal-700">Current resume: {file.name}. Choose another file to replace it.</p>}</label>
        <label className="block"><span className="text-sm font-semibold">2. Paste the job description</span><textarea value={jobDescription} onChange={e => setJobDescription(e.target.value)} placeholder="Paste the responsibilities, requirements, and skills here..." className="mt-4 h-40 w-full resize-none rounded-xl border border-slate-300 p-3 text-sm outline-none ring-teal-500 focus:ring-2" /></label>
        <div className="md:col-span-2">{error && <p role="alert" className="mb-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}<button disabled={loading} className="rounded-xl bg-teal-600 px-5 py-3 font-semibold text-white transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-60">{loading ? 'Analyzing your resume…' : 'Analyze Resume'}</button></div>
      </form> : <section className="space-y-6">
        <div className="rounded-3xl bg-ink p-7 text-white"><p className="text-sm font-semibold text-mint">SKILL SIMILARITY SCORE</p><div className="mt-4 flex flex-col gap-5 sm:flex-row sm:items-center"><ScoreRing score={result.score} /><p className="max-w-3xl leading-7 text-slate-200">{result.job_skills.length ? `${result.matched_skills.length} of ${result.job_skills.length} recognized job skills are present in the resume. ${result.explanation}` : 'No skills from the editable dictionary were recognized in the job description, so a skill similarity score cannot be calculated.'}</p></div></div>
        <div className="grid gap-4 md:grid-cols-3"><SkillList title="Matched skills" skills={result.matched_skills} tone="green" /><SkillList title="Missing job skills" skills={result.missing_skills} tone="amber" /><SkillList title="Skills in your resume" skills={result.resume_skills} /></div>
        <div className="flex flex-wrap items-center gap-3"><button onClick={editAnalysis} className="rounded-xl bg-teal-600 px-5 py-3 font-semibold text-white hover:bg-teal-700">Edit resume or job description</button><button onClick={reset} className="rounded-xl border border-slate-300 bg-white px-5 py-3 font-semibold text-slate-700 hover:bg-slate-50">Start a new analysis</button>{result.history_message && <p className="text-sm text-slate-500">{result.history_message}</p>}</div>
      </section>}
      <section className="mt-12 border-t border-slate-200 pt-8"><div className="flex items-baseline justify-between"><div><h2 className="text-xl font-bold">Recent analysis history</h2><p className="mt-1 text-sm text-slate-500">Your latest 20 saved comparisons. Resume text is never stored.</p></div>{history?.available && <span className="text-sm text-teal-700">Saved to MongoDB</span>}</div>{error && <p role="alert" className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</p>}{history?.available && history.items?.length ? <div className="mt-5 grid gap-4 md:grid-cols-2">{history.items.map(item => <HistoryCard key={item.id} item={item} onDelete={deleteHistoryItem} deleting={deletingId === item.id} />)}</div> : <p className="mt-3 text-sm text-slate-500">{history?.message || 'No saved analyses yet. Configure MongoDB to enable history.'}</p>}</section>
      <p className="mt-12 text-center text-xs leading-5 text-slate-500">Skill results use a small editable dictionary and are not a complete understanding of natural language.</p>
    </div>
  </main>
}
export default App

