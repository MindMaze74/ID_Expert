variable "cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
}
variable "folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
}
variable "zone" {
  description = "Availability zone"
  type        = string
  default     = "ru-central1-a"
}
variable "yc_token" {
  description = "Yandex Cloud IAM token"
  type        = string
  sensitive   = true
  default     = ""
}
variable "ssh_public_key" {
  description = "Public SSH key for VMs"
  type        = string
  sensitive   = true
}
variable "bastion_name" {
  description = "Bastion VM name"
  type        = string
  default     = "bastion"
}
variable "monitoring_name" {
  description = "Monitoring VM name"
  type        = string
  default     = "monitoring"
}
variable "bastion_resources" {
  description = "Bastion VM resources"
  type = object({
    cores  = number
    memory = number
  })
  default = {
    cores  = 2
    memory = 4
  }
}
variable "monitoring_resources" {
  description = "Monitoring VM resources"
  type = object({
    cores  = number
    memory = number
  })
  default = {
    cores  = 4
    memory = 8
  }
}
variable "my_ip" {
  description = "Your external IP for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}
