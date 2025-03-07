/* ������ �� ��������� ������ ������������ �� id*/
SELECT 
	users.id, 
	login, 
	password, 
	users.name, 
	group_id, 
	groups.name 
FROM users 
INNER JOIN groups ON users.group_id = groups.id 
WHERE users.id = 123;

/* ������ �� ��������� ���������� */
SELECT 
	date, 
	room, 
	teachers.name as teacher, 
	subjects.name as subject, 
	time_type as class, times.
	time_from as ts, 
	times.time_to as te 
	FROM schedule 
INNER JOIN teachers ON teacher_id = teachers.id 
INNER JOIN subjects ON subject_id = subjects.id
INNER JOIN times ON time_type = times.id
WHERE group_id = 1

/* ���������� ������ � ������� times */
INSERT INTO `times`(`time_from`, `time_to`) VALUES ('8:30','10:00');
INSERT INTO `times`(`time_from`, `time_to`) VALUES ('10:10','11:40');
INSERT INTO `times`(`time_from`, `time_to`) VALUES ('12:00','13:30');
INSERT INTO `times`(`time_from`, `time_to`) VALUES ('13:50','15:20');
INSERT INTO `times`(`time_from`, `time_to`) VALUES ('15:30','17:00');
INSERT INTO `times`(`time_from`, `time_to`) VALUES ('17:10','18:20');

/* ���������� ������� � ������� subjects */
INSERT INTO `subjects`(`name`) VALUES ('����������� ���� � ���������������� ������������');
INSERT INTO `subjects`(`name`) VALUES ('���������� ��������');
INSERT INTO `subjects`(`name`) VALUES ('��������� � ������������ ����������� �������');
INSERT INTO `subjects`(`name`) VALUES ('�������� ����������� ���������������� ������������');
INSERT INTO `subjects`(`name`) VALUES ('���������� ��������� ����������');
INSERT INTO `subjects`(`name`) VALUES ('��������� ����������������');
INSERT INTO `subjects`(`name`) VALUES ('���������� ���������� ������������ �����������');
