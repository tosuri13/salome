.PHONY: deploy cleanup

cleanup:
	@echo "🧹 Cleaning up CDK Docker images..."
	@docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "^cdk" | xargs -r docker rmi -f 2>/dev/null || true

deploy: cleanup
	@echo "🚀 Deploying CDK stack..."
	cd libs/salome-cdk && cdk deploy
