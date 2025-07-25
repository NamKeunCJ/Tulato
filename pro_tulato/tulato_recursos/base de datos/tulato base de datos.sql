CREATE TABLE "usuario" (
  "usuario_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "nombre" VARCHAR(50) NOT NULL,
  "apellido" VARCHAR(50) NOT NULL,
  "correo" VARCHAR(100) UNIQUE NOT NULL,
  "contraseña" VARCHAR(260) NOT NULL,
  "edad" INT NOT NULL,
  "genero_id" INT NOT NULL,
  "discapacidad" VARCHAR(100) NOT NULL,
  "grupo_etnico" VARCHAR(100),
  "rol_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "rol" (
  "rol_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "tipo" VARCHAR(50) UNIQUE NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "genero" (
  "genero_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "tipo" VARCHAR(50) UNIQUE NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "contenido" (
  "contenido_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "titulo" VARCHAR(100) NOT NULL,
  "descripcion" TEXT NOT NULL,
  "coordenada" VARCHAR(100) NOT NULL,
  "imagen" VARCHAR(999),
  "rol_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "asociacion_contenido" (
  "asociacion_contenido_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "contenido_id" INT NOT NULL,
  "determinante_id" INT NOT NULL,
  "vereda_id" INT NOT NULL,
  "municipio_id" INT NOT NULL,
  "proyecto_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "determinante" (
  "determinante_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "tipo" VARCHAR(100) NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "vereda" (
  "vereda_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "nombre" VARCHAR(100) NOT NULL,
  "municipio_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "municipio" (
  "municipio_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "nombre" VARCHAR(100) NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "proyecto" (
  "proyecto_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "nombre" VARCHAR(255) NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "test" (
  "test_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "nombre" VARCHAR(255) NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "pregunta" (
  "pregunta_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "enunciado" TEXT NOT NULL,
  "test_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "opcion" (
  "opcion_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "respuesta" TEXT NOT NULL,
  "es_correcta" INT NOT NULL,
  "pregunta_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "intento_test" (
  "intento_test_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "puntaje" TEXT NOT NULL,
  "intento" INT NOT NULL,
  "usuario_id" INT NOT NULL,
  "test_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "descarga" (
  "descarga_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "cantidad" INT NOT NULL,
  "usuario_id" INT NOT NULL,
  "contenido_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

CREATE TABLE "visualizacion" (
  "visualizacion_id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY NOT NULL,
  "canidad" INT NOT NULL,
  "usuario_id" INT NOT NULL,
  "contenido_id" INT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "update_at" TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  "deleted_at" TIMESTAMP,
  "status" BOOLEAN NOT NULL
);

ALTER TABLE "usuario" ADD FOREIGN KEY ("genero_id") REFERENCES "genero" ("genero_id");

ALTER TABLE "usuario" ADD FOREIGN KEY ("rol_id") REFERENCES "rol" ("rol_id");

ALTER TABLE "contenido" ADD FOREIGN KEY ("rol_id") REFERENCES "rol" ("rol_id");

ALTER TABLE "asociacion_contenido" ADD FOREIGN KEY ("contenido_id") REFERENCES "contenido" ("contenido_id");

ALTER TABLE "asociacion_contenido" ADD FOREIGN KEY ("determinante_id") REFERENCES "determinante" ("determinante_id");

ALTER TABLE "asociacion_contenido" ADD FOREIGN KEY ("vereda_id") REFERENCES "vereda" ("vereda_id");

ALTER TABLE "asociacion_contenido" ADD FOREIGN KEY ("municipio_id") REFERENCES "municipio" ("municipio_id");

ALTER TABLE "asociacion_contenido" ADD FOREIGN KEY ("proyecto_id") REFERENCES "proyecto" ("proyecto_id");

ALTER TABLE "vereda" ADD FOREIGN KEY ("municipio_id") REFERENCES "municipio" ("municipio_id");

ALTER TABLE "pregunta" ADD FOREIGN KEY ("test_id") REFERENCES "test" ("test_id");

ALTER TABLE "opcion" ADD FOREIGN KEY ("pregunta_id") REFERENCES "pregunta" ("pregunta_id");

ALTER TABLE "intento_test" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("usuario_id");

ALTER TABLE "intento_test" ADD FOREIGN KEY ("test_id") REFERENCES "test" ("test_id");

ALTER TABLE "descarga" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("usuario_id");

ALTER TABLE "descarga" ADD FOREIGN KEY ("contenido_id") REFERENCES "contenido" ("contenido_id");

ALTER TABLE "visualizacion" ADD FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("usuario_id");

ALTER TABLE "visualizacion" ADD FOREIGN KEY ("contenido_id") REFERENCES "contenido" ("contenido_id");
