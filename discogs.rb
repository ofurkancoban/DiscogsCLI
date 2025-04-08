class Discogs < Formula
  include Language::Python::Virtualenv

  desc "Discogs Data Processor CLI"
  homepage "https://github.com/ofurkancoban/discogs-cli"
  url "https://github.com/ofurkancoban/discogs-cli/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "<SHA256-HASH>" # bu release tar.gz dosyasının hash'i
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"discogs", "--help"
  end
end