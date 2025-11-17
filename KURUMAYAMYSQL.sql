CREATE DATABASE Kurumaya;

CREATE TABLE Cliente (
  id INT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  data_nascimento DATE  
);

CREATE TABLE veiculos (
	placa VARCHAR(7) PRIMARY KEY,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    ano YEAR,
    categoria VARCHAR(100),
    preco FLOAT,
    imagem BLOB
    );

CREATE TABLE estoque (
	placa VARCHAR(7),
    FOREIGN KEY (placa) REFERENCES veiculos(placa)
);

CREATE TABLE contratos (
	id INT,
    FOREIGN KEY (id) REFERENCES cliente(id),
	placa VARCHAR(7),
    FOREIGN KEY (placa) REFERENCES veiculos(placa),
    id_aluguel INT PRIMARY KEY,
    tempo INT,
    VALOR FLOAT
);