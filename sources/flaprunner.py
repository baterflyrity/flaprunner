import sys
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired

import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse
from loguru import logger
from subprocrunner import SubprocessRunner

app = FastAPI()
projects_root = Path.cwd() / 'projects'
with open('log.txt', 'a', encoding='utf8') as f:
	f.write('\n\n\n')
logger.configure(handlers=[{
	"sink":   sys.stdout,
	"format": "[{time:DD.MM.YYYY HH:mm:ss}]\t{level}\t{message}",
	'level':  'INFO'
}, {
	"sink":        'log.txt',
	'rotation':    '2 months',
	'retention':   '6 months',
	'compression': 'zip',
	"format":      "[{time:DD.MM.YYYY HH:mm:ss}]\t{level}\t{message}",
	'backtrace':   True,
	'diagnose':    True,
	'level':       'INFO'
}])


@app.get('/')
def get_root():
	return RedirectResponse('/docs')


@app.get('/run/{project}/{job}')
def run(project: str, job: str, timeout: float = 3600) -> PlainTextResponse:
	logger.info(f'Requested job {project}/{job}.')
	project_path = projects_root / project
	if not project_path.is_dir():
		logger.info(f'Can not find project {project}.')
		raise HTTPException(400, f'Can not find project {project}.')
	job_path = project_path / '.flaprunner' / f'{job}.sh'
	if not job_path.is_file():
		logger.info(f'Can not find job {job} in project {project}.')
		raise HTTPException(400, f'Can not find job {job} in project {project}.')
	runner = SubprocessRunner(f'/bin/sh "{job_path.resolve()}"')
	return_code = '(unknown)'
	try:
		return_code = runner.run(timeout=timeout, shell=True, check=True, cwd=project_path)
	except (CalledProcessError, TimeoutExpired) as e:
		logger.info(f'Job {job} in project {project} failed with exit code {return_code}: {e}\n\n{runner.stderr}'.strip())
		raise HTTPException(500, f'Job {job} in project {project} failed with exit code {return_code}: {e}\n\n{runner.stderr}'.strip())
	else:
		logger.info(f'Job {project}/{job} done.')
		logger.trace(f'{runner.stderr}\n\n{runner.stdout}'.strip())
		return PlainTextResponse(f'{runner.stderr}\n\n{runner.stdout}'.strip())


def main(interface: str = '', port: int = 39393, projects: Path = projects_root):
	global projects_root
	projects_root = projects
	logger.info(f'Hosting {projects.resolve()}')
	logger.info(f'Listening {interface}:{port}')
	uvicorn.run(app, host=interface, port=port)


if __name__ == '__main__':
	cli = typer.Typer(add_completion=False)
	cli.command()(main)
	cli()
