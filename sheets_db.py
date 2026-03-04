import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

SUPABASE_URL = "https://hjferypqgslbrbfeklmm.supabase.co"
SUPABASE_KEY = "sb_secret_xIMlvvwrM4-uMgY_ZnGddg_x5H0rYbh"

class SheetsDB:
    def __init__(self):
        self.db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self._init_tables()

    def _init_tables(self):
        pass  # Tablas creadas manualmente en Supabase SQL Editor

    # ── PRODUCTOS ──────────────────────────────────────────────
    def get_productos(self) -> pd.DataFrame:
        all_data = []
        offset = 0
        limit = 1000
        while True:
            res = self.db.table("productos").select("*").order("nombre").range(offset, offset + limit - 1).execute()
            if not res.data:
                break
            all_data.extend(res.data)
            if len(res.data) < limit:
                break
            offset += limit
        if not all_data:
            return pd.DataFrame(columns=["id","codigo","nombre","cajon","stock","stock_minimo","fecha_vencimiento","fecha_creacion"])
        df = pd.DataFrame(all_data)
        df['stock']        = pd.to_numeric(df['stock'],        errors='coerce').fillna(0).astype(int)
        df['stock_minimo'] = pd.to_numeric(df['stock_minimo'], errors='coerce').fillna(5).astype(int)
        if 'fecha_vencimiento' not in df.columns:
            df['fecha_vencimiento'] = None
        return df

    def add_producto(self, codigo, nombre, cajon, stock=0, stock_minimo=5, fecha_vencimiento=None):
        try:
            data = {
                "codigo": str(codigo),
                "nombre": str(nombre),
                "cajon": str(cajon),
                "stock": int(stock),
                "stock_minimo": int(stock_minimo),
                "fecha_creacion": datetime.now().isoformat()
            }
            if fecha_vencimiento:
                data["fecha_vencimiento"] = str(fecha_vencimiento)
            self.db.table("productos").upsert(data, on_conflict="codigo").execute()
        except Exception:
            pass

    def actualizar_stock(self, producto_id, nuevo_stock):
        self.db.table("productos").update({"stock": int(nuevo_stock)}).eq("id", int(producto_id)).execute()

    def actualizar_vencimiento(self, producto_id, fecha_vencimiento):
        self.db.table("productos").update({
            "fecha_vencimiento": str(fecha_vencimiento) if fecha_vencimiento else None
        }).eq("id", int(producto_id)).execute()

    # ── MOVIMIENTOS ────────────────────────────────────────────
    def get_movimientos(self) -> pd.DataFrame:
        res = self.db.table("movimientos").select("*").order("fecha").execute()
        if not res.data:
            return pd.DataFrame(columns=["id","producto_id","producto_codigo",
                                         "producto_nombre","cajon","tipo","cantidad","nota","fecha"])
        df = pd.DataFrame(res.data)
        df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
        return df

    def registrar_movimiento(self, producto_id, codigo, nombre, cajon, tipo, cantidad, nota=""):
        self.db.table("movimientos").insert({
            "producto_id":      int(producto_id),
            "producto_codigo":  str(codigo),
            "producto_nombre":  str(nombre),
            "cajon":            str(cajon),
            "tipo":             str(tipo),
            "cantidad":         int(cantidad),
            "nota":             str(nota),
            "fecha":            datetime.now().isoformat()
        }).execute()
