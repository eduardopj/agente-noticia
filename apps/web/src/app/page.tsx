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
  updated_at: string | null;
  updated_at_br: string | null;
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

type ClassifiedGroup = {
  key: string;
  title: string;
  description: string;
  sources: Source[];
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
  searchParams?: Promise<{ date?: string; grupo?: string }>;
}) {
  const params = await searchParams;
  const episodes = await fetchJson<Episode[]>("/episodes", []);
  const selectedDate = params?.date;
  const selectedGroup = params?.grupo || "todos";
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

  const pendingInEpisode = sources.filter((source) => source.validation_status === "pending").length;
  const trustedInEpisode = sources.filter((source) => source.validation_status === "trusted").length;
  const groups = buildSourceGroups(sources);
  const visibleGroups =
    selectedGroup === "todos" ? groups : groups.filter((group) => group.key === selectedGroup);
  const categoryCards = buildCategoryCards(sources);
  const episodeUrl = activeEpisode ? `/?date=${activeEpisode.episode_date}` : "/";

  return (
    <main>
      <header className="shellHeader">
        <div>
          <p className="eyebrow">Radar diario</p>
          <h1>Tech IA</h1>
          <p className="subtitle">
            Noticias, IA, tecnologia global, videos e pesquisa academica em uma central diaria de validacao.
          </p>
        </div>
        <div className="liveBadge">
          <span>WhatsApp</span>
          <strong>{labelWhatsapp(activeEpisode?.whatsapp_status)}</strong>
        </div>
      </header>

      <section className="homeGrid">
        <article className="spotlight">
          <div className="spotlightCopy">
            <p className="eyebrow">Episodio em destaque</p>
            <span className="date">{activeEpisode ? activeEpisode.episode_date_br : "Nenhum episodio gerado"}</span>
            <h2>{activeEpisode?.title || "Aguardando o primeiro radar"}</h2>
            <p>
              {activeEpisode?.executive_summary ||
                "Execute o job diario para coletar noticias, videos e artigos academicos."}
            </p>
            <div className="heroActions">
              <a href="#briefing">Ler resumo</a>
              <a href="#fontes">Validar fontes</a>
              {activeEpisode?.audio_url ? <a href={activeEpisode.audio_url}>Ouvir audio</a> : null}
            </div>
          </div>
          <div className="episodePlayer">
            <span>Resumo e audio</span>
            <strong>{activeEpisode?.episode_date_short_br || "--/--/----"}</strong>
            {activeEpisode?.audio_url ? <audio controls src={activeEpisode.audio_url} /> : <p>Audio ainda nao gerado.</p>}
            <a href={episodeUrl}>Link deste episodio</a>
          </div>
        </article>

        <aside className="episodeLibrary">
          <div className="sectionHeader compact">
            <p className="eyebrow">Todos os episodios</p>
            <h3>Historico diario</h3>
          </div>
          <div className="episodeList">
            {episodes.length === 0 ? (
              <p className="empty">Nenhum registro diario ainda.</p>
            ) : (
              episodes.map((item) => (
                <Link
                  className={`episodeRow ${activeEpisode?.id === item.id ? "active" : ""}`}
                  href={`/?date=${item.episode_date}`}
                  key={item.id}
                >
                  <span>{item.episode_date_short_br}</span>
                  <strong>{item.title}</strong>
                  <small>
                    {formatUsd(item.estimated_cost_usd)} / {formatBrl(item.estimated_cost_brl)}
                  </small>
                </Link>
              ))
            )}
          </div>
        </aside>
      </section>

      <section className="statsGrid">
        <StatCard label="Episodios" value={stats.episodes} />
        <StatCard label="Fontes salvas" value={stats.sources} />
        <StatCard label="Academicas" value={stats.academic_sources} />
        <StatCard label="Custo deste episodio" value={`${formatUsd(activeEpisode?.estimated_cost_usd || 0)} / ${formatBrl(activeEpisode?.estimated_cost_brl || 0)}`} />
      </section>

      <section className="classificationPanel">
        <div className="sectionHeader compact">
          <p className="eyebrow">Classificacoes</p>
          <h3>Assuntos e fontes deste episodio</h3>
        </div>
        <div className="classificationGrid">
          {categoryCards.map((card) => (
            <a href={`#${card.anchor}`} className="classificationCard" key={card.key}>
              <span>{card.label}</span>
              <strong>{card.count}</strong>
              <small>{card.description}</small>
            </a>
          ))}
        </div>
      </section>

      <section className="costPanel">
        <div>
          <span>Uso do episodio</span>
          <strong>
            Texto: {(activeEpisode?.summary_input_tokens || 0) + (activeEpisode?.script_input_tokens || 0)} tokens de entrada,{" "}
            {(activeEpisode?.summary_output_tokens || 0) + (activeEpisode?.script_output_tokens || 0)} de saida. Audio:{" "}
            {activeEpisode?.estimated_audio_minutes?.toFixed(1) || "0.0"} min estimados.
          </strong>
        </div>
        <div>
          <span>Validacao</span>
          <strong>
            {trustedInEpisode} aprovadas | {pendingInEpisode} pendentes
          </strong>
        </div>
      </section>

      <section className="grid">
        <article className="briefing" id="briefing">
          <div className="sectionHeader">
            <p className="eyebrow">Briefing</p>
            <h3>Resumo, contexto e proximos passos</h3>
          </div>
          <pre>{activeEpisode?.briefing_markdown || "Sem briefing disponivel."}</pre>
        </article>

        <aside className="sources" id="fontes">
          <div className="sectionHeader sourceHeader">
            <div>
              <p className="eyebrow">Validacao</p>
              <h3>Fontes organizadas</h3>
            </div>
            {activeEpisode ? (
              <form action={validateEpisodeSources}>
                <input name="episodeId" type="hidden" value={activeEpisode.id} />
                <button name="status" type="submit" value="trusted">Aprovar tudo</button>
              </form>
            ) : null}
          </div>
          <nav className="sourceFilters">
            <Link className={selectedGroup === "todos" ? "active" : ""} href={`/?date=${activeEpisode?.episode_date || ""}#fontes`}>
              Todas
            </Link>
            {groups.map((group) => (
              <Link
                className={selectedGroup === group.key ? "active" : ""}
                href={`/?date=${activeEpisode?.episode_date || ""}&grupo=${group.key}#fontes`}
                key={group.key}
              >
                {group.title}
              </Link>
            ))}
          </nav>
          <div className="sourceList">
            {sources.length === 0 ? (
              <p className="empty">Nenhuma fonte coletada ainda.</p>
            ) : (
              visibleGroups.map((group) => <SourceGroup group={group} key={group.key} />)
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

function SourceGroup({ group }: { group: ClassifiedGroup }) {
  if (group.sources.length === 0) return null;
  return (
    <div className="sourceGroup" id={group.key}>
      <h4>
        {group.title}
        <small>{group.description}</small>
      </h4>
      {group.sources.map((source) => (
        <div className="sourceItem" key={source.id}>
          <div className="sourceMeta">
            <span>{source.source_name}</span>
            <em className={`pill ${source.validation_status}`}>{labelValidation(source.validation_status)}</em>
          </div>
          <a href={source.url} rel="noreferrer" target="_blank">
            <strong>{source.title}</strong>
          </a>
          <small>
            {labelCategory(source.category)} | {source.source_type} | confiabilidade {source.reliability_score.toFixed(1)}
          </small>
          {source.authors ? <small>Autores: {source.authors}</small> : null}
          {source.published_at_br ? <small>Publicado em: {source.published_at_br}</small> : null}
          {source.updated_at_br ? <small>Atualizado em: {source.updated_at_br}</small> : null}
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

function buildSourceGroups(sources: Source[]): ClassifiedGroup[] {
  const definitions: Omit<ClassifiedGroup, "sources">[] = [
    { key: "academicas", title: "Academicas", description: "Papers, revistas e indexadores cientificos." },
    { key: "portais-br", title: "Portais BR", description: "Canaltech, TecMundo, Tecnoblog e portais nacionais." },
    { key: "jornais", title: "Jornais", description: "Cobertura jornalistica e impacto publico." },
    { key: "videos", title: "Videos", description: "Canais do YouTube e conteudo em video." },
    { key: "fontes-primarias", title: "Primarias", description: "Blogs oficiais, empresas, laboratorios e projetos." },
    { key: "globais", title: "Mundo", description: "Portais internacionais de tecnologia e mercado." },
    { key: "infra-seguranca", title: "Infra e seguranca", description: "Chips, cloud, devtools e ciberseguranca." },
    { key: "outras", title: "Outras", description: "Itens relevantes fora dos grupos principais." },
  ];
  return definitions
    .map((definition) => ({
      ...definition,
      sources: sources.filter((source) => classifySource(source) === definition.key),
    }))
    .filter((group) => group.sources.length > 0);
}

function buildCategoryCards(sources: Source[]) {
  const groups = buildSourceGroups(sources);
  return groups.map((group) => ({
    key: group.key,
    anchor: group.key,
    label: group.title,
    count: group.sources.length,
    description: group.description,
  }));
}

function classifySource(source: Source) {
  if (source.category === "academico" || source.source_type === "paper" || source.source_type === "academic_press") {
    return "academicas";
  }
  if (source.source_type === "video" || source.category.startsWith("video_")) {
    return "videos";
  }
  if (source.source_type === "primary") {
    return "fontes-primarias";
  }
  if (source.source_name.toLowerCase().includes("g1") || source.source_name.toLowerCase().includes("folha")) {
    return "jornais";
  }
  if (source.source_type === "press_br" || source.category.includes("brasil")) {
    return "portais-br";
  }
  if (["devtools", "hardware_ia", "seguranca", "open_source"].includes(source.category)) {
    return "infra-seguranca";
  }
  if (source.source_type === "press" || source.category.includes("global")) {
    return "globais";
  }
  return "outras";
}

function labelCategory(category: string) {
  const labels: Record<string, string> = {
    academico: "academico",
    brasil_tecnologia: "tecnologia no Brasil",
    brasil_negocios_tech: "negocios tech no Brasil",
    ia_global: "IA global",
    tecnologia_global: "tecnologia global",
    open_source: "open source",
    devtools: "devtools",
    hardware_ia: "hardware e IA",
    seguranca: "seguranca",
    video_brasil: "video brasileiro",
    video_global: "video global",
  };
  return labels[category] || category;
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
