module babel (
	clk,
	reset,
	charIn,
	setSeed,
	charOut
);
	reg _sv2v_0;
	parameter PageSize = 0;
	input clk;
	input reset;
	input [4:0] charIn;
	input setSeed;
	input [4:0] charOut;
	reg [7:0] counter;
	reg [4:0] state;
	reg [4:0] nextState [0:1];
	always @(*) begin : randgen
		if (_sv2v_0)
			;
		if (setSeed)
			nextState[0] = state ^ (state << 2);
		else
			nextState[0] = charIn ^ (state << 2);
		nextState[1] = nextState[0] ^ (nextState[0] >> 1);
		nextState[2] = nextState[1] ^ (nextState[1] << 3);
	end
	wire pageEnd;
	assign pageEnd = counter == -1;
	always @(posedge clk) begin : registers
		if (reset) begin
			state <= 0;
			counter <= 0;
		end
		else if (pageEnd) begin
			state <= nextState[2];
			counter <= counter + 1;
		end
	end
	assign charOut = (pageEnd ? 0 : state);
	initial _sv2v_0 = 0;
endmodule
module babel (
	clk,
	reset,
	charIn,
	setSeed,
	charOut
);
	reg _sv2v_0;
	input clk;
	input reset;
	input [4:0] charIn;
	input setSeed;
	input [4:0] charOut;
	reg [7:0] counter;
	reg [4:0] state;
	reg [4:0] nextState [0:1];
	always @(*) begin : randgen
		if (_sv2v_0)
			;
		if (setSeed)
			nextState[0] = state ^ (state << 2);
		else
			nextState[0] = charIn ^ (state << 2);
		nextState[1] = nextState[0] ^ (nextState[0] >> 1);
		nextState[2] = nextState[1] ^ (nextState[1] << 3);
	end
	wire pageEnd;
	assign pageEnd = counter == -1;
	always @(posedge clk) begin : registers
		if (reset) begin
			state <= 0;
			counter <= 0;
		end
		else if (pageEnd) begin
			state <= nextState[2];
			counter <= counter + 1;
		end
	end
	assign charOut = (pageEnd ? 0 : state);
	initial _sv2v_0 = 0;
endmodule
