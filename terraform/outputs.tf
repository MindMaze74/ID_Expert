output "bastion_public_ip" {
  value = yandex_compute_instance.bastion.network_interface.0.nat_ip_address
}
output "monitoring_private_ip" {
  value = yandex_compute_instance.monitoring.network_interface.0.ip_address
}
output "grafana_url" {
  value = "http://${yandex_compute_instance.bastion.network_interface.0.nat_ip_address}:3000"
}
output "prometheus_url" {
  value = "http://${yandex_compute_instance.bastion.network_interface.0.nat_ip_address}:9090"
}
