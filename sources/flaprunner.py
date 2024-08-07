"""Flap Runner - is job runner service with simple REST web API."""
import sys
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired
from typing import Self

import typer
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, RedirectResponse
from loguru import logger
from subprocrunner import SubprocessRunner

app = FastAPI()
projects_root = Path.cwd() / 'projects'
with open('log.txt', 'a', encoding='utf8') as f:
	f.write('\n\n\n')
logger.configure(handlers=[{
	"sink"  : sys.stdout,
	"format": "[{time:DD.MM.YYYY HH:mm:ss}]\t{level}\t{message}",
	'level' : 'INFO'
}, {
	"sink"       : 'log.txt',
	'rotation'   : '2 months',
	'retention'  : '6 months',
	'compression': 'zip',
	"format"     : "[{time:DD.MM.YYYY HH:mm:ss}]\t{level}\t{message}",
	'backtrace'  : True,
	'diagnose'   : True,
	'level'      : 'INFO'
}])


class default:
	def __init__(self, default_value: ..., *, key: list | tuple | None = None):
		self.key = key
		self.default_value = default_value

	def __ror__(self, other: list | tuple):
		return default(self.default_value, key=other)


class ConfigTree:
	def __init__(self, data: dict | None = None, *, raw_data: dict[tuple, ...]|None = None):
		self.data: dict[tuple, ...] = raw_data or {}
		if data:
			self._load_settings(data)

	def _load_settings(self, structure: dict, path: list | None = None) -> None:
		if path is None:
			path = []
		for key, value in structure.items():
			subpath = path + [key]
			if isinstance(value, dict):
				self._load_settings(value, subpath)
			else:
				self.data[tuple(subpath)] = value

	def __getitem__(self, key: list | tuple | default) -> ...:
		if isinstance(key, default):
			return self.data.get(tuple(key.key), key.default_value)
		return self.data[tuple(key)]

	def __setitem__(self, key: list | tuple, value: ...) -> None:
		self.data[tuple(key)] = value

	def __or__(self, other: Self) -> Self:
		return ConfigTree(raw_data=self.data | other.data)

	def __str__(self):
		return str(self.data)

	def __repr__(self):
		return f'{self.__class__.__name__}({repr(self.data)})'


default_project_config = ConfigTree({
	'access': {
		'auth_required': False,
		'tokens'       : [],  
	}
})
instance_project_config = ConfigTree()


@app.get('/')
def get_root():
	return RedirectResponse('/docs')


@app.get('/run/{project}/{job}')
def run(project: str, job: str, timeout: float = 3600, access_token: str = '') -> PlainTextResponse:
	logger.info(f'Requested job {project}/{job}.')
	project_path = projects_root / project
	if not project_path.is_dir():
		logger.info(f'Can not find project {project}.')
		raise HTTPException(400, f'Can not find project {project}.')
	project_config = get_project_config(project)
	if project_config[['access', 'auth_required']]:
		if access_token not in project_config[['access', 'tokens']]:
			raise HTTPException(403, f'Incorrect access token for project {project}.')
	job_path = project_path / '.flaprunner' / f'{job}.sh'
	if not job_path.is_file():
		logger.info(f'Can not find job {job} in project {project}.')
		raise HTTPException(400, f'Can not find job {job} in project {project}.')
	runner = SubprocessRunner(f'/bin/sh -c "cd \"{project_path.resolve()}\" && /bin/sh \"{job_path.resolve()}\""')
	return_code = '(unknown)'
	try:
		return_code = runner.run(timeout=timeout, shell=True, check=True)
	except (CalledProcessError, TimeoutExpired) as e:
		logger.info(
				f'Job {job} in project {project} failed with exit code {return_code}: {e}\n\n{runner.stderr}'.strip())
		raise HTTPException(500,
							f'Job {job} in project {project} failed with exit code {return_code}: {e}\n\n{runner.stderr}'.strip())
	else:
		logger.info(f'Job {project}/{job} done.')
		logger.trace(f'{runner.stderr}\n\n{runner.stdout}'.strip())
		return PlainTextResponse(f'{runner.stderr}\n\n{runner.stdout}'.strip())


def get_config(path: Path) -> ConfigTree | None:
	if path.is_file():
		try:
			if isinstance(data := yaml.safe_load(path.read_text('utf8')), dict):
				return ConfigTree(data)
			else:
				raise TypeError(f'Parsed config from {path} must be dictionary but {type(data)} was loaded.')
		except Exception as e:
			logger.info(f'Can not parse config at {path}: {e}')


def merge_projetc_configs(*configs: ConfigTree) -> ConfigTree:
	if len(configs) == 1:
		return configs[0]
	elif len(configs) == 0:
		raise ValueError('Not enought configs to merge.')
	elif len(configs) > 2:
		return merge_projetc_configs(merge_projetc_configs(*configs[:2]), *configs[2:])
	else:
		cfg1, cfg2 = configs
		# Step 1: override and extend
		result = cfg1 | cfg2
		# Step 2: merge sensitive settings
		# result[['access', 'tokens']] = cfg1[['access', 'tokens'] | default([])] + cfg2[['access', 'tokens'] | default([])]  # union tokens instead of overriding
		return result


def get_project_config(project: str) -> ConfigTree:
	if (project_config_data := get_config(Path(projects_root) / project / ".flaprunner" / "flaprunner.yaml")) is None:
		project_config_data = ConfigTree()
	return merge_projetc_configs(default_project_config, instance_project_config, project_config_data)


def main(interface: str = '', port: int = 39393, projects: Path = projects_root):
	global projects_root, instance_project_config
	projects_root = projects
	logger.info(f'Hosting {projects.resolve()}')
	if (cfg := get_config(projects / 'flaprunner.yaml')) is not None:
		instance_project_config = cfg
		logger.info('Loaded instance config.')
	logger.info(f'Listening {interface}:{port}')
	uvicorn.run(app, host=interface, port=port)


if __name__ == '__main__':
	cli = typer.Typer(add_completion=False)
	cli.command()(main)
	cli()
