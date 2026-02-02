FROM ghcr.io/astral-sh/uv:0.9.26 AS uv
FROM public.ecr.aws/lambda/python:3.14 AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_INSTALLER_METADATA=1
ENV UV_LINK_MODE=copy

RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv export --all-packages --frozen --no-emit-workspace --no-dev --no-editable -o requirements.txt && \
    uv pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=libs,target=libs \
    uv export --all-packages --frozen --no-dev --no-editable -o requirements.txt && \
    uv pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

FROM public.ecr.aws/lambda/python:3.14

COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}
COPY apps ${LAMBDA_TASK_ROOT}
