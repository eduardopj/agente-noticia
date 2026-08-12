import asyncio

from radar_api.agents import run_daily_pipeline


if __name__ == "__main__":
    episode = asyncio.run(run_daily_pipeline())
    print(f"Episodio gerado: {episode.episode_date} #{episode.id}")
