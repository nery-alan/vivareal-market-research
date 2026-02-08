#!/usr/bin/env python3
"""
Tool: Report Generator
Gera relatório Excel com análise de mercado imobiliário.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class ReportGenerator:
    def __init__(self, input_file: str = "data/processed/listings.json",
                 output_dir: str = "reports"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> pd.DataFrame:
        """Carrega dados do JSON e converte para DataFrame."""
        print(f"📂 Carregando dados: {self.input_file}")

        if not self.input_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.input_file}")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not data:
            raise ValueError("Arquivo JSON vazio ou sem dados válidos")

        df = pd.DataFrame(data)

        print(f"✅ {len(df)} registros carregados")
        return df

    def validate_data(self, df: pd.DataFrame, min_count: int = 100) -> bool:
        """Valida se os dados atendem aos requisitos."""
        print(f"\n🔍 Validando dados...")

        # Verificar colunas obrigatórias
        required_cols = ['link', 'price', 'area', 'price_per_sqm']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"❌ Colunas faltando: {missing_cols}")
            return False

        # Verificar quantidade mínima
        if len(df) < min_count:
            print(f"⚠️  Apenas {len(df)} anúncios (mínimo: {min_count})")
            return False

        # Verificar valores nulos
        null_counts = df[required_cols].isnull().sum()
        if null_counts.any():
            print(f"⚠️  Valores nulos encontrados:")
            print(null_counts[null_counts > 0])

        print(f"✅ Validação OK: {len(df)} anúncios válidos")
        return True

    def calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """Calcula estatísticas descritivas."""
        stats = {
            "total_listings": len(df),
            "price": {
                "mean": df['price'].mean(),
                "median": df['price'].median(),
                "min": df['price'].min(),
                "max": df['price'].max(),
                "std": df['price'].std()
            },
            "area": {
                "mean": df['area'].mean(),
                "median": df['area'].median(),
                "min": df['area'].min(),
                "max": df['area'].max()
            },
            "price_per_sqm": {
                "mean": df['price_per_sqm'].mean(),
                "median": df['price_per_sqm'].median(),
                "min": df['price_per_sqm'].min(),
                "max": df['price_per_sqm'].max()
            }
        }

        return stats

    def print_summary(self, stats: Dict):
        """Imprime resumo estatístico."""
        print(f"\n📊 Resumo Estatístico:")
        print(f"\n   Total de Anúncios: {stats['total_listings']}")

        print(f"\n   💰 Preço Total:")
        print(f"      Média:   R$ {stats['price']['mean']:,.2f}")
        print(f"      Mediana: R$ {stats['price']['median']:,.2f}")
        print(f"      Mínimo:  R$ {stats['price']['min']:,.2f}")
        print(f"      Máximo:  R$ {stats['price']['max']:,.2f}")

        print(f"\n   📏 Área (m²):")
        print(f"      Média:   {stats['area']['mean']:.1f} m²")
        print(f"      Mediana: {stats['area']['median']:.1f} m²")

        print(f"\n   📐 Preço por m²:")
        print(f"      Média:   R$ {stats['price_per_sqm']['mean']:,.2f}/m²")
        print(f"      Mediana: R$ {stats['price_per_sqm']['median']:,.2f}/m²")
        print(f"      Mínimo:  R$ {stats['price_per_sqm']['min']:,.2f}/m²")
        print(f"      Máximo:  R$ {stats['price_per_sqm']['max']:,.2f}/m²")

    def generate_excel(self, df: pd.DataFrame, filename: str = None) -> Path:
        """
        Gera arquivo Excel com os dados.

        Colunas: Link, Valor (R$), Tamanho (m²), Valor/m²
        """
        # Preparar DataFrame para export
        export_df = df[['link', 'price', 'area', 'price_per_sqm']].copy()

        # Renomear colunas para português
        export_df.columns = ['Link', 'Valor (R$)', 'Tamanho (m²)', 'Valor/m²']

        # Ordenar por valor total (crescente)
        export_df = export_df.sort_values('Valor (R$)')

        # Resetar index
        export_df.reset_index(drop=True, inplace=True)

        # Gerar nome do arquivo
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vivareal_freguesia_do_o_{timestamp}.xlsx"

        output_path = self.output_dir / filename

        # Salvar Excel
        print(f"\n💾 Gerando Excel: {output_path}")

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet principal com dados
            export_df.to_excel(writer, sheet_name='Anúncios', index=False)

            # Formatar colunas
            worksheet = writer.sheets['Anúncios']

            # Ajustar larguras
            worksheet.column_dimensions['A'].width = 60  # Link
            worksheet.column_dimensions['B'].width = 15  # Valor
            worksheet.column_dimensions['C'].width = 15  # Área
            worksheet.column_dimensions['D'].width = 15  # Valor/m²

            # Aplicar formato de moeda (colunas B e D)
            for row in range(2, len(export_df) + 2):
                worksheet[f'B{row}'].number_format = 'R$ #,##0.00'
                worksheet[f'D{row}'].number_format = 'R$ #,##0.00'

        print(f"✅ Excel gerado com sucesso!")
        print(f"   📍 Localização: {output_path.absolute()}")
        print(f"   📊 Linhas: {len(export_df)}")

        return output_path

    def generate_report(self, min_count: int = 100) -> Path:
        """
        Executa pipeline completo de geração de relatório.

        Returns:
            Caminho do arquivo Excel gerado
        """
        print("\n🚀 Gerando Relatório de Pesquisa de Mercado\n")

        # Carregar dados
        df = self.load_data()

        # Validar
        if not self.validate_data(df, min_count):
            raise ValueError(f"Dados não atendem aos requisitos mínimos (min: {min_count} anúncios)")

        # Calcular estatísticas
        stats = self.calculate_statistics(df)
        self.print_summary(stats)

        # Gerar Excel
        excel_path = self.generate_excel(df)

        print(f"\n🎉 Relatório concluído com sucesso!")

        return excel_path


def main():
    """CLI para execução standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Excel report from listings")
    parser.add_argument("--input", default="data/processed/listings.json", help="JSON de entrada")
    parser.add_argument("--output-dir", default="reports", help="Diretório de saída")
    parser.add_argument("--min-count", type=int, default=100, help="Mínimo de anúncios")
    parser.add_argument("--filename", help="Nome do arquivo Excel (opcional)")

    args = parser.parse_args()

    generator = ReportGenerator(
        input_file=args.input,
        output_dir=args.output_dir
    )

    try:
        excel_path = generator.generate_report(min_count=args.min_count)
        print(f"\n✅ Sucesso! Abra o arquivo: {excel_path}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        exit(1)


if __name__ == "__main__":
    main()
