type Episode = {
  id: number;
  episode_date: string;
  title: string;
  executive_summary: string;
  briefing_markdown: string;
  script_markdown: string | null;
  audio_url: string | null;
  whatsapp_status: string;
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
const timezone = process.env.TIMEZONE || "America/Rio_Branco";

function formatDateBr(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: timezone,
  }).format(new Date(`${value}T12:00:00`));
}

async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${apiUrl}${path}`, { next: { revalidate: 60 } });
    if (!response.ok) return fallback;
    return response.json();
  } catch {
    return fallback;
  }
}

export default async function Home() {
  const episode = await fetchJson<Episode | null>("/episodes/latest", null);
  const sources = await fetchJson<Source[]>("/sources", []);
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
          <p className="eyebrow">Radar diário</p>
          <h1>Tech IA</h1>
        </div>
        <div className="status">
          <span>WhatsApp</span>
          <strong>{episode?.whatsapp_status === "sent" ? "enviado" : "pendente"}</strong>
        </div>
      </header>

      <section className="hero">
        <div>
          <p className="date">{episode ? formatDateBr(episode.episode_date) : "Nenhum episódio gerado"}</p>
          <h2>{episode?.title || "Aguardando o primeiro radar"}</h2>
          <p>{episode?.executive_summary || "Execute o job diário para coletar notícias e artigos acadêmicos."}</p>
        </div>
        <div className="audioPanel">
          <span>Áudio do dia</span>
          {episode?.audio_url ? (
            <audio controls src={episode.audio_url} />
          ) : (
            <p>Áudio ainda não gerado. Configure OPENAI_API_KEY para ativar TTS.</p>
          )}
        </div>
      </section>

      <section className="statsGrid">
        <StatCard label="Episódios" value={stats.episodes} />
        <StatCard label="Fontes" value={stats.sources} />
        <StatCard label="Acadêmicas" value={stats.academic_sources} />
        <StatCard label="Validação pendente" value={stats.pending_validation} />
      </section>

      <section className="grid">
        <article className="briefing">
          <div className="sectionHeader">
            <p className="eyebrow">Briefing</p>
            <h3>Resumo e contexto</h3>
          </div>
          <pre>{episode?.briefing_markdown || "Sem briefing disponível."}</pre>
        </article>

        <aside className="sources">
          <div className="sectionHeader">
            <p className="eyebrow">Validação</p>
            <h3>Fontes recentes</h3>
          </div>
          <div className="sourceList">
            {sources.length === 0 ? (
              <p className="empty">Nenhuma fonte coletada ainda.</p>
            ) : (
              <>
                <SourceGroup title="Artigos acadêmicos" sources={academicSources.slice(0, 10)} />
                <SourceGroup title="Notícias e tecnologia" sources={generalSources.slice(0, 10)} />
              </>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
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
        <a className="sourceItem" href={source.url} key={source.id} rel="noreferrer" target="_blank">
          <span>{source.source_name}</span>
          <strong>{source.title}</strong>
          <small>
            {source.category} | {source.source_type} | confiabilidade {source.reliability_score.toFixed(1)}
          </small>
          <small>Status: {labelValidation(source.validation_status)}</small>
        </a>
      ))}
    </div>
  );
}

function labelValidation(status: string) {
  const labels: Record<string, string> = {
    pending: "pendente",
    trusted: "confiável",
    doubtful: "duvidosa",
    discarded: "descartada",
  };
  return labels[status] || status;
}
