grammar MySQL;

inicio: creacion usar tabla+ cerrar;

creacion: CREAR ID;
usar: USAR ID;
tabla: TABLA ID INICIO campo+ foreign_key* FIN;
campo: ID (NUMERICO | ALFABETICO | FECHA);
foreign_key: ID DEPENDE ID;
cerrar: CERRAR;

DEPENDE: 'dependeDe';
CERRAR: 'cerrar';
NUMERICO: 'numeros';
ALFABETICO: 'letras';
FECHA: 'fecha';
TABLA: 'tabla';
INICIO: 'inicio';
FIN: 'fin';
USAR: 'usar';
CREAR: 'crear';

ID: ('a' ..'z' | 'A' ..'Z' | '_') (
		'a' ..'z'
		| 'A' ..'Z'
		| '0' ..'9'
		| '_'
	)*;
WS: (' ' | '\n' | '\t' | '\r')+ -> skip;