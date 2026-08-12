import Link from "next/link";
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
  estimated_cost_brl: number;
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

async function validateEpisodeSources(formData: FormData) {
  "use server";
  const episodeId = formData.get("episodeId");
  const status = formData.get("status");
  if (!episodeId || !status) return;
  await fetch(`${apiUrl}/episodes/${episodeId}/sources/validation`, {
    method: "POST",
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

export default async function Home({
  searchParams,
}: {
  searchParams?: Promise<{ date?: string }>;
}) {
  const params = await searchParams;
  const episodes = await fetchJson<Episode[]>("/episodes", []);
  const selectedDate = params?.date;
  const episode = selectedDate
    ? await fetchJson<Episode | null>(`/episodes/${selectedDate}`, null)
    : await fetchJson<Episode | null>("/episodes/latest", null);
  const activeEpisode = episode || episodes[0] || null;
  const sources = activeEpisode
    ? await fetchJson<Source[]>(`/episodes/${activeEpisode.id}/sources`, [])
    : [];
  const stats = await fetchJson<Stats>("/stats", {
    episodes: 0,
    sources: 0,
    academic_sources: 0,
    pending_validation: 0,
  });

  const academicSources = sources.filter((source) => source.category === "academico");
  const generalSources = sources.filter((source) => source.category !== "academico");
  const pendingInEpisode = sources.filter((source) => source.validation_status === "pending").length;

  return (
    <main>
      <header className="shellHeader">
        <div>
          <p className="eyebrow">Radar diario</p>
          <h1>Tech IA</h1>
          <p className="subtitle">Noticias, IA, tecnologia global, videos e pesquisa academica em um painel unico.</p>
        </div>
        <div className="liveBadge">
          <span>WhatsApp</span>
          <strong>{labelWhatsapp(activeEpisode?.whatsapp_status)}</strong>
        </div>
      </header>

      <section className="hero">
        <div className="heroMain">
          <p className="date">{activeEpisode ? activeEpisode.episode_date_br : "Nenhum episodio gerado"}</p>
          <h2>{activeEpisode?.title || "Aguardando o primeiro radar"}</h2>
          <p>{activeEpisode?.executive_summary || "Execute o job diario para coletar noticias, videos e artigos academicos."}</p>
          <div className="heroActions">
            <a href="#fontes">Validar fontes</a>
            {activeEpisode?.audio_url ? <a href={activeEpisode.audio_url}>Ouvir audio</a> : null}
          </div>
        </div>
        <div className="audioPanel">
          <span>Audio do dia</span>
          {activeEpisode?.audio_url ? (
            <audio controls src={activeEpisode.audio_url} />
          ) : (
            <p>Audio ainda nao gerado.</p>
          )}
        </div>
      </section>

      <section className="statsGrid">
        <StatCard label="Episodios" value={stats.episodes} />
        <StatCard label="Fontes salvas" value={stats.sources} />
        <StatCard label="Pendentes neste dia" value={pendingInEpisode} />
        <StatCard label="Custo estimado" value={`${formatUsd(activeEpisode?.estimated_cost_usd || 0)} / ${formatBrl(activeEpisode?.estimated_cost_brl || 0)}`} />
      </section>

      <section className="costPanel">
        <div>
          <span>Uso do episodio</span>
          <strong>
            Texto: {(activeEpisode?.summary_input_tokens || 0) + (activeEpisode?.script_input_tokens || 0)} tokens de entrada,
            {" "}
            {(activeEpisode?.summary_output_tokens || 0) + (activeEpisode?.script_output_tokens || 0)} de saida.
            {" "}
            Audio: {activeEpisode?.estimated_audio_minutes?.toFixed(1) || "0.0"} min estimados.
          </strong>
        </div>
        <div>
          <span>Gerado em</span>
          <strong>{activeEpisode?.created_at_br || "Aguardando geracao"}</strong>
        </div>
      </section>

      <section className="historyPanel">
        <div className="sectionHeader compact">
          <p className="eyebrow">Historico</p>
          <h3>Tudo que ja foi gerado</h3>
        </div>
        <div className="episodeStrip">
          {episodes.length === 0 ? (
            <p className="empty">Nenhum registro diario ainda.</p>
          ) : (
            episodes.map((item) => (
              <Link
                className={`episodeCard ${activeEpisode?.id === item.id ? "active" : ""}`}
                href={`/?date=${item.episode_date}`}
                key={item.id}
              >
                <span>{item.episode_date_short_br}</span>
                <strong>{formatUsd(item.estimated_cost_usd)} / {formatBrl(item.estimated_cost_brl)}</strong>
                <small>{labelWhatsapp(item.whatsapp_status)}</small>
              </Link>
            ))
          )}
        </div>
      </section>

      <section className="grid">
        <article className="briefing">
          <div className="sectionHeader">
            <p className="eyebrow">Briefing</p>
            <h3>Resumo e contexto</h3>
          </div>
          <pre>{activeEpisode?.briefing_markdown || "Sem briefing disponivel."}</pre>
        </article>

        <aside className="sources" id="fontes">
          <div className="sectionHeader sourceHeader">
            <div>
              <p className="eyebrow">Validacao</p>
              <h3>Fontes deste episodio</h3>
            </div>
            {activeEpisode ? (
              <form action={validateEpisodeSources}>
                <input name="episodeId" type="hidden" value={activeEpisode.id} />
                <button name="status" type="submit" value="trusted">Aprovar tudo</button>
              </form>
            ) : null}
          </div>
          <div className="sourceList">
            {sources.length === 0 ? (
              <p className="empty">Nenhuma fonte coletada ainda.</p>
            ) : (
              <>
                <SourceGroup title="Noticias, videos e tecnologia" sources={generalSources} />
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
    <div className="statCard">
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
          <div className="sourceMeta">
            <span>{source.source_name}</span>
            <em className={`pill ${source.validation_status}`}>{labelValidation(source.validation_status)}</em>
          </div>
          <a href={source.url} rel="noreferrer" target="_blank">
            <strong>{source.title}</strong>
          </a>
          <small>
            {source.category} | {source.source_type} | confiabilidade {source.reliability_score.toFixed(1)}
          </small>
          {source.published_at_br ? <small>Publicado em: {source.published_at_br}</small> : null}
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

function formatUsd(value: number) {
  return `US$ ${value.toFixed(4)}`;
}

function formatBrl(value: number) {
  return `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
