output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.web_n8n_host.public_ip
}

output "webserver_url" {
  description = "Web server URL"
  value       = "http://${aws_instance.web_n8n_host.public_ip}:8080"
}

output "n8n_url" {
  description = "n8n URL"
  value       = "http://${aws_instance.web_n8n_host.public_ip}:5678"
}
