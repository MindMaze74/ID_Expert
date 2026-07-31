terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.zone
  token     = var.yc_token != "" ? var.yc_token : null
}

resource "yandex_vpc_network" "main" {
  name = "monitoring-network"
}

resource "yandex_vpc_subnet" "public" {
  name           = "public-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.main.id
  v4_cidr_blocks = ["10.0.1.0/24"]
}

resource "yandex_vpc_subnet" "private" {
  name           = "private-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.main.id
  v4_cidr_blocks = ["10.0.2.0/24"]
  route_table_id = yandex_vpc_route_table.nat.id
}

resource "yandex_vpc_gateway" "nat" {
  name = "nat-gateway"
  shared_egress_gateway {}
}

resource "yandex_vpc_route_table" "nat" {
  name       = "nat-route"
  network_id = yandex_vpc_network.main.id
  static_route {
    destination_prefix = "0.0.0.0/0"
    gateway_id         = yandex_vpc_gateway.nat.id
  }
}

resource "yandex_vpc_security_group" "bastion" {
  name        = "bastion-sg"
  description = "Bastion host security group"
  network_id  = yandex_vpc_network.main.id
  ingress {
    protocol    = "TCP"
    port        = 22
    v4_cidr_blocks = [var.my_ip]
    description = "SSH from my IP"
  }
  ingress {
    protocol    = "TCP"
    port        = 3000
    v4_cidr_blocks = [var.my_ip]
    description = "Grafana proxy"
  }
  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Allow all outgoing"
  }
}

resource "yandex_vpc_security_group" "monitoring" {
  name        = "monitoring-sg"
  description = "Monitoring services security group"
  network_id  = yandex_vpc_network.main.id
  ingress {
    protocol       = "TCP"
    port           = 1883
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "MQTT from external"
  }
  ingress {
    protocol       = "TCP"
    port           = 9090
    v4_cidr_blocks = ["10.0.0.0/16"]
    description    = "Prometheus internal"
  }
  ingress {
    protocol       = "TCP"
    port           = 3000
    v4_cidr_blocks = ["10.0.0.0/16"]
    description    = "Grafana internal"
  }
  ingress {
    protocol       = "TCP"
    port           = 9125
    v4_cidr_blocks = ["10.0.0.0/16"]
    description    = "MQTT exporter metrics"
  }
  ingress {
    protocol       = "TCP"
    port           = 9100
    v4_cidr_blocks = ["10.0.0.0/16"]
    description    = "Node Exporter"
  }
  ingress {
    protocol       = "TCP"
    port           = 22
    v4_cidr_blocks = ["10.0.0.0/16"]
    description    = "SSH from internal network"
  }
  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Allow all outgoing"
  }
}

data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_compute_instance" "bastion" {
  name        = var.bastion_name
  zone        = var.zone
  platform_id = "standard-v3"
  resources {
    cores  = var.bastion_resources.cores
    memory = var.bastion_resources.memory
  }
  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 30
    }
  }
  network_interface {
    subnet_id          = yandex_vpc_subnet.public.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.bastion.id]
  }
  metadata = {
    ssh-keys = "ubuntu:${var.ssh_public_key}"
  }
}

resource "yandex_compute_instance" "monitoring" {
  name        = var.monitoring_name
  zone        = var.zone
  platform_id = "standard-v3"
  resources {
    cores  = var.monitoring_resources.cores
    memory = var.monitoring_resources.memory
  }
  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 50
    }
  }
  network_interface {
    subnet_id          = yandex_vpc_subnet.private.id
    nat                = false
    security_group_ids = [yandex_vpc_security_group.monitoring.id]
  }
  metadata = {
    ssh-keys = "ubuntu:${var.ssh_public_key}"
  }
}
