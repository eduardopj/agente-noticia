import { revalidatePath } from "next/cache";

type Episode = {
  id: number;
  episode_date: string;
  episode_date_br: string;
  episode_date_short_br: string;
  title: string;
  executive_summary: string;
  briefing_markdown: string;
  script_markdown: string | null;
  audio_url: string | null;
  whatsapp_status: string;
  created_at_br: string;
  summary_input_tokens: number;
  summary_output_tokens: number;
  script_input_tokens: number;
  script_output_tokens: number;
  tts_input_chars: number;
  estimated_audio_minutes: number;
  estimated_cost_usd: number;
};

type Source = {
  id: number;
  title: string;
  url: string;
  source_name: string;
  source_type: string;
  language: string;
  category: string;
  authors: string | null;
  published_at: string | null;
  published_at_br: string | null;
  collected_at_br: string;
  raw_summary: string | null;
  curated_summary: string | null;
  impact: string | null;
  relevance_score: number;
  reliability_score: number;
  novelty_score: number;
  validation_status: string;
};

type Stats = {
  episodes: number;
  sources: number;
  academic_sources: number;
  pending_validation: number;
};

const apiUrl = process.env.API_BASE_URL || "http://localhost:8000";

async function validateSource(formData: FormData) {
  "use server";
  const sourceId = formData.get("sourceId");
  const status = formData.get("status");
  if (!sourceId || !status) return;
  await fetch(`${apiUrl}/sources/${sourceId}/validation`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  revalidatePath("/");
}

async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${apiUrl}${path}`, { cache: "no-store" });
    if (!response.ok) return fallback;
    return response.json();
  } catch {
    return fallback;
  }
}

export default async function Home() {
  const episode = await fetchJson<Episode | null>("/episodes/latest", null);
  const sources = episode
    ? await fetchJson<Source[]>(`/episodes/${episode.id}/sources`, [])
    : [];
  const stats = await fetchJson<Stats>("/stats", {
    episodes: 0,
    sources: 0,
    academic_sources: 0,
    pending_validation: 0,
  });

  const academicSources = sources.filter((source) => source.category === "academico");
  const generalSources = sources.filter((source) => source.category !== "academico");

  return (
    <main>
      <header className="topbar">
        <div>
          <p className="eyebrow">Radar diario</p>
          <h1>Tech IA</h1>
        </div>
        <div className="status">
          <span>WhatsApp</span>
          <strong>{labelWhatsapp(episode?.whatsapp_status)}</strong>
        </div>
      </header>

      <section className="hero">
        <div>
          <p className="date">{episode ? episode.episode_date_br : "Nenhum episodio gerado"}</p>
          <h2>{episode?.title || "Aguardando o primeiro radar"}</h2>
          <p>{episode?.executive_summary || "Execute o job diario para coletar noticias e artigos academicos."}</p>
        </div>
        <div className="audioPanel">
          <span>Audio do dia</span>
          {episode?.audio_url ? (
            <audio controls src={episode.audio_url} />
          ) : (
            <p>Audio ainda nao gerado. Configure OPENAI_API_KEY para ativar TTS.</p>
          )}
        </div>
      </section>

      <section className="statsGrid">
        <StatCard label="Episodios" value={stats.episodes} />
        <StatCard label="Fontes" value={stats.sources} />
        <StatCard label="Pendentes" value={stats.pending_validation} />
        <StatCard label="Custo estimado" value={`US$ ${(episode?.estimated_cost_usd || 0).toFixed(4)}`} />
      </section>

      <section className="costPanel">
        <span>Uso do episodio</span>
        <strong>
          Texto: {(episode?.summary_input_tokens || 0) + (episode?.script_input_tokens || 0)} tokens de entrada,
          {" "}
          {(episode?.summary_output_tokens || 0) + (episode?.script_output_tokens || 0)} de saida.
          {" "}
          Audio: {episode?.estimated_audio_minutes?.toFixed(1) || "0.0"} min estimados.
        </strong>
      </section>

      <section className="grid">
        <article className="briefing">
          <div className="sectionHeader">
            <p className="eyebrow">Briefing</p>
            <h3>Resumo e contexto</h3>
          </div>
          <pre>{episode?.briefing_markdown || "Sem briefing disponivel."}</pre>
        </article>

        <aside className="sources">
          <div className="sectionHeader">
            <p className="eyebrow">Validacao</p>
            <h3>Fontes deste episodio</h3>
          </div>
          <div className="sourceList">
            {sources.length === 0 ? (
              <p className="empty">Nenhuma fonte coletada ainda.</p>
            ) : (
              <>
                <SourceGroup title="Noticias e tecnologia" sources={generalSources} />
                <SourceGroup title="Artigos academicos" sources={academicSources} />
              </>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SourceGroup({ title, sources }: { title: string; sources: Source[] }) {
  if (sources.length === 0) return null;
  return (
    <div className="sourceGroup">
      <h4>{title}</h4>
      {sources.map((source) => (
        <div className="sourceItem" key={source.id}>
          <span>{source.source_name}</span>
          <a href={source.url} rel="noreferrer" target="_blank">
            <strong>{source.title}</strong>
          </a>
          <small>
            {source.category} | {source.source_type} | confiabilidade {source.reliability_score.toFixed(1)}
          </small>
          {source.published_at_br ? <small>Publicado em: {source.published_at_br}</small> : null}
          <small>Status: {labelValidation(source.validation_status)}</small>
          <form action={validateSource} className="validationActions">
            <input name="sourceId" type="hidden" value={source.id} />
            <button name="status" type="submit" value="trusted">Confiavel</button>
            <button name="status" type="submit" value="doubtful">Duvidosa</button>
            <button name="status" type="submit" value="discarded">Descartar</button>
          </form>
        </div>
      ))}
    </div>
  );
}

function labelValidation(status?: string) {
  const labels: Record<string, string> = {
    pending: "pendente",
    trusted: "confiavel",
    doubtful: "duvidosa",
    discarded: "descartada",
  };
  return labels[status || "pending"] || status;
}

function labelWhatsapp(status?: string) {
  const labels: Record<string, string> = {
    sent: "texto e audio enviados",
    sent_text_only: "texto enviado",
    not_sent: "pendente",
  };
  return labels[status || "not_sent"] || status;
}
